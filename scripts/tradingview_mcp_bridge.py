#!/usr/bin/env python3
"""
TradingView MCP Signal Bridge Worker
====================================
Bridge script that reads real-time indicator data from local TradingView Desktop
via tradingview-mcp, evaluates trading strategy rules, and dispatches webhook
signals to the Trading Bot Backend (/api/webhook/tradingview).

All configuration is loaded from the project's .env file — no hardcoded paths.

Usage (auto-reads from .env):
    python scripts/tradingview_mcp_bridge.py

Usage (override via CLI args):
    python scripts/tradingview_mcp_bridge.py --bot-config "My_Bot" --interval 5.0
"""

import os
import sys
import json
import time
import argparse
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any

# ── Load .env from project root ──────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

def load_dotenv(env_path: Path):
    """Minimal .env loader — no external dependency required."""
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value

load_dotenv(PROJECT_ROOT / ".env")

# ── Setup logging ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TV_MCP_Bridge")


class TradingViewMCPBridge:
    def __init__(
        self,
        mcp_path: str,
        backend_url: str,
        bot_config: str,
        passphrase: Optional[str] = None,
        poll_interval: float = 3.0,
        rsi_buy_threshold: float = 30.0,
        rsi_sell_threshold: float = 70.0
    ):
        self.mcp_path = Path(mcp_path).resolve()
        self.backend_url = backend_url.rstrip("/")
        self.webhook_endpoint = f"{self.backend_url}/api/webhook/tradingview"
        self.bot_config = bot_config
        self.passphrase = passphrase
        self.poll_interval = poll_interval
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        self.cli_entry = self.mcp_path / "src" / "cli" / "index.js"
        self.last_signal_action = None

    def verify_environment(self) -> bool:
        """Verify tradingview-mcp CLI exists and can connect to TradingView Desktop."""
        if not self.cli_entry.exists():
            logger.error(f"tradingview-mcp CLI not found at: {self.cli_entry}")
            logger.error("Set MCP_REPO_PATH in .env to the correct clone path of tradingview-mcp.")
            return False

        try:
            res = subprocess.run(
                ["node", str(self.cli_entry), "status"],
                capture_output=True, text=True, timeout=10
            )
            if res.returncode == 0 and res.stdout.strip():
                data = json.loads(res.stdout)
                if data.get("success"):
                    logger.info("✅ Connected to TradingView via MCP!")
                    logger.info(f"   Target: {data.get('target_title', 'Unknown')}")
                    return True
                else:
                    logger.warning(f"⚠️  MCP connected but TradingView not ready: {data.get('error')}")
                    logger.warning("Make sure TradingView is running with --remote-debugging-port=9222")
                    return False
            return False
        except FileNotFoundError:
            logger.error("Node.js not found. Please install Node.js 18+ and ensure 'node' is in PATH.")
            return False
        except Exception as e:
            logger.error(f"Failed to verify environment: {e}")
            return False

    def _run_cli(self, *args, timeout: int = 10) -> Optional[str]:
        """Run a tradingview-mcp CLI command and return stdout."""
        try:
            res = subprocess.run(
                ["node", str(self.cli_entry), *args],
                capture_output=True, text=True, timeout=timeout
            )
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
            return None
        except Exception as e:
            logger.debug(f"CLI error ({' '.join(args)}): {e}")
            return None

    def fetch_chart_values(self) -> Optional[Dict[str, Any]]:
        """Fetch current study/indicator values from TradingView Desktop via MCP CLI."""
        raw = self._run_cli("values")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.debug(f"Could not parse chart values JSON: {raw[:200]}")
            return None

    def fetch_price_quote(self) -> Optional[Dict[str, Any]]:
        """Fetch current ticker price from TradingView Desktop via MCP CLI."""
        raw = self._run_cli("quote")
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def send_webhook_signal(self, symbol: str, action: str, details: Optional[Dict] = None) -> bool:
        """Send JSON payload to Trading Bot Backend /api/webhook/tradingview."""
        payload: Dict[str, Any] = {
            "symbol": symbol,
            "action": action,
            "config": self.bot_config,
        }
        if self.passphrase:
            payload["passphrase"] = self.passphrase
        if details:
            payload["details"] = details

        logger.info(f"🚀 Dispatching Signal → action={action.upper()}, symbol={symbol}")
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_endpoint,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                logger.info(f"✅ Webhook accepted (HTTP {resp.status}): {body[:200]}")
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8") if e.fp else ""
            logger.error(f"❌ Webhook HTTP {e.code}: {e.reason} — {body[:200]}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"❌ Cannot reach backend at {self.backend_url}: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending webhook: {e}")
            return False

    def evaluate_strategy_and_dispatch(self, data: Dict[str, Any], quote: Optional[Dict] = None):
        """
        Evaluate RSI strategy rule and dispatch signal when triggered.
        Extend this method to add more complex multi-indicator strategies.
        """
        symbol = (quote or {}).get("symbol") or data.get("symbol", "UNKNOWN")

        # ── Extract RSI from study values ──
        rsi_val: Optional[float] = None
        studies = data.get("studies") or data.get("indicators") or data.get("values") or []
        if isinstance(studies, dict):
            studies = list(studies.values())

        for study in (studies if isinstance(studies, list) else []):
            name = str(study.get("name", "")).upper()
            if "RSI" in name or "RELATIVE STRENGTH" in name:
                vals = study.get("values") or study.get("value")
                try:
                    if isinstance(vals, (int, float)):
                        rsi_val = float(vals)
                    elif isinstance(vals, dict):
                        rsi_val = float(next(iter(vals.values())))
                    elif isinstance(vals, list) and vals:
                        rsi_val = float(vals[0])
                except (TypeError, ValueError):
                    pass
                break

        if rsi_val is not None:
            logger.info(f"📊 [{symbol}] RSI = {rsi_val:.2f} (Buy<{self.rsi_buy_threshold}, Sell>{self.rsi_sell_threshold})")
            action = None
            if rsi_val <= self.rsi_buy_threshold:
                action = "buy"
            elif rsi_val >= self.rsi_sell_threshold:
                action = "sell"

            if action and action != self.last_signal_action:
                success = self.send_webhook_signal(symbol, action, {"rsi": rsi_val, "source": "MCP_Bridge"})
                if success:
                    self.last_signal_action = action
        else:
            logger.info(f"📊 [{symbol}] Values received. RSI not detected among visible indicators.")

    def run(self):
        """Main polling loop."""
        logger.info("=" * 52)
        logger.info("   TradingView MCP Signal Bridge — Starting")
        logger.info(f"   Webhook  : {self.webhook_endpoint}")
        logger.info(f"   Bot      : {self.bot_config}")
        logger.info(f"   Interval : {self.poll_interval}s")
        logger.info(f"   MCP Path : {self.mcp_path}")
        logger.info("=" * 52)

        if not self.verify_environment():
            logger.error("Environment check failed. Exiting.")
            sys.exit(1)

        logger.info("Bridge is running. Press Ctrl+C to stop.\n")
        try:
            while True:
                values = self.fetch_chart_values()
                quote = self.fetch_price_quote()
                if values or quote:
                    self.evaluate_strategy_and_dispatch(values or {}, quote)
                else:
                    logger.warning("No data received from TradingView. Is the Desktop app open with debug port 9222?")
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            logger.info("\n🛑 Bridge stopped by user.")


def main():
    parser = argparse.ArgumentParser(
        description="TradingView MCP Signal Bridge — reads from .env by default"
    )
    parser.add_argument("--mcp-path",    default=os.environ.get("MCP_REPO_PATH", "./tradingview-mcp"))
    parser.add_argument("--backend-url", default=os.environ.get("MCP_BACKEND_URL", "http://localhost:8000"))
    parser.add_argument("--bot-config",  default=os.environ.get("MCP_BOT_CONFIG", ""))
    parser.add_argument("--passphrase",  default=os.environ.get("WEBHOOK_PASSPHRASE"))
    parser.add_argument("--interval",    type=float, default=float(os.environ.get("MCP_POLL_INTERVAL", "3.0")))
    parser.add_argument("--rsi-buy",     type=float, default=float(os.environ.get("MCP_RSI_BUY_THRESHOLD", "30.0")))
    parser.add_argument("--rsi-sell",    type=float, default=float(os.environ.get("MCP_RSI_SELL_THRESHOLD", "70.0")))
    args = parser.parse_args()

    if not args.bot_config:
        logger.error("❌ MCP_BOT_CONFIG is not set in .env and --bot-config was not provided.")
        sys.exit(1)

    TradingViewMCPBridge(
        mcp_path=args.mcp_path,
        backend_url=args.backend_url,
        bot_config=args.bot_config,
        passphrase=args.passphrase,
        poll_interval=args.interval,
        rsi_buy_threshold=args.rsi_buy,
        rsi_sell_threshold=args.rsi_sell
    ).run()


if __name__ == "__main__":
    main()
