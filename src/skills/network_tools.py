"""Network tools skill – DNS lookup, port check, and hostname utilities.

Covers the "DevOps & Cloud" category from the awesome-openclaw-skills
directory.  Uses Python stdlib only (``socket``).

Supported actions
-----------------
dns_lookup      Resolve a hostname to IP addresses.
reverse_dns     Reverse-lookup an IP address to hostname.
port_check      Test if a TCP port is reachable (connect attempt).
my_hostname     Return the local machine's hostname and IP.
"""

from __future__ import annotations

import socket


_CONNECT_TIMEOUT = 5  # seconds


class NetworkToolsSkill:
    """DNS lookups, port checks, and basic network utilities."""

    name = "network_tools"
    description = (
        "Network utilities (no external APIs – uses stdlib socket). "
        "Supported actions: 'dns_lookup' (host); 'reverse_dns' (ip); "
        "'port_check' (host, port); 'my_hostname'."
    )

    def run(
        self,
        action: str,
        host: str = "",
        ip: str = "",
        port: int = 80,
    ) -> str:
        """
        Perform a network operation.

        Parameters
        ----------
        action:
            One of ``"dns_lookup"``, ``"reverse_dns"``,
            ``"port_check"``, ``"my_hostname"``.
        host:
            Hostname or IP for ``"dns_lookup"`` and ``"port_check"``.
        ip:
            IP address string for ``"reverse_dns"``.
        port:
            TCP port number for ``"port_check"`` (default 80).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "dns_lookup":
            return self._dns_lookup(host)
        if action == "reverse_dns":
            return self._reverse_dns(ip or host)
        if action == "port_check":
            return self._port_check(host, port)
        if action == "my_hostname":
            return self._my_hostname()
        return (
            f"Error: unknown action {action!r}. "
            "Use dns_lookup, reverse_dns, port_check, or my_hostname."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dns_lookup(host: str) -> str:
        if not host:
            return "Error: host is required for dns_lookup"
        try:
            results = socket.getaddrinfo(host, None)
            ips = sorted({r[4][0] for r in results})
            return f"{host} → {', '.join(ips)}"
        except socket.gaierror as exc:
            return f"Error: DNS lookup failed for {host!r} – {exc}"

    @staticmethod
    def _reverse_dns(ip: str) -> str:
        if not ip:
            return "Error: ip is required for reverse_dns"
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return f"{ip} → {hostname}"
        except socket.herror as exc:
            return f"Error: reverse DNS failed for {ip!r} – {exc}"

    @staticmethod
    def _port_check(host: str, port: int) -> str:
        if not host:
            return "Error: host is required for port_check"
        try:
            with socket.create_connection((host, int(port)), timeout=_CONNECT_TIMEOUT):
                return f"{host}:{port} is OPEN"
        except ConnectionRefusedError:
            return f"{host}:{port} is CLOSED (connection refused)"
        except OSError as exc:
            return f"{host}:{port} is UNREACHABLE – {exc}"

    @staticmethod
    def _my_hostname() -> str:
        try:
            name = socket.gethostname()
            ip = socket.gethostbyname(name)
            return f"hostname: {name}\nip: {ip}"
        except socket.error as exc:
            return f"Error: {exc}"
