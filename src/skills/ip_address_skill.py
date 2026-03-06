"""IP address skill – validate, classify, and do subnet math on IP addresses.

Covers the "DevOps & Cloud" and "Network & Security" categories.
Uses Python stdlib ``ipaddress`` module only.

Supported actions
-----------------
validate        Check if a string is a valid IPv4 or IPv6 address.
classify        Classify an IP (private, public, loopback, multicast, etc.).
to_int          Convert an IP address to its integer representation.
from_int        Convert an integer to an IP address string.
network_info    Parse a CIDR network (e.g. 192.168.0.0/24) and show details.
hosts           List hosts in a small CIDR network (max 256).
contains        Check if an IP is in a CIDR network.
supernet        Get the supernet one prefix-length up.
version         Return 4 or 6 for the IP version.
expand_ipv6     Expand a compressed IPv6 address to full notation.
"""

from __future__ import annotations

import ipaddress


class IpAddressSkill:
    """Validate, classify, and do subnet math on IP addresses."""

    name = "ip_address"
    description = (
        "IP address utilities. "
        "Supported actions: 'validate' (ip); 'classify' (ip); "
        "'to_int' (ip); 'from_int' (number, version=4); "
        "'network_info' (network, e.g. 192.168.0.0/24); "
        "'hosts' (network); 'contains' (network, ip); "
        "'supernet' (network); 'version' (ip); 'expand_ipv6' (ip)."
    )

    def run(
        self,
        action: str,
        ip: str = "",
        network: str = "",
        number: int = 0,
        version: int = 4,
    ) -> str:
        """
        Perform an IP address operation.

        Parameters
        ----------
        action:
            The operation to perform (see description).
        ip:
            IP address string.
        network:
            CIDR network string (e.g. ``"192.168.1.0/24"``).
        number:
            Integer for ``"from_int"``.
        version:
            IP version for ``"from_int"`` (4 or 6; default 4).

        Returns
        -------
        str
            Result string or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        try:
            if action == "validate":
                return self._validate(ip)
            if action == "classify":
                return self._classify(ip)
            if action == "to_int":
                return self._to_int(ip)
            if action == "from_int":
                return self._from_int(number, version)
            if action == "network_info":
                return self._network_info(network or ip)
            if action == "hosts":
                return self._hosts(network or ip)
            if action == "contains":
                return self._contains(network, ip)
            if action == "supernet":
                return self._supernet(network or ip)
            if action == "version":
                return self._version(ip)
            if action == "expand_ipv6":
                return self._expand_ipv6(ip)
        except Exception as exc:
            return f"Error: {exc}"

        return (
            f"Error: unknown action {action!r}. "
            "Use validate, classify, to_int, from_int, network_info, "
            "hosts, contains, supernet, version, or expand_ipv6."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ip(ip: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        if not ip:
            raise ValueError("ip is required")
        return ipaddress.ip_address(ip.strip())

    @staticmethod
    def _parse_net(net: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
        if not net:
            raise ValueError("network is required")
        return ipaddress.ip_network(net.strip(), strict=False)

    def _validate(self, ip: str) -> str:
        if not ip:
            return "Error: ip is required"
        try:
            addr = ipaddress.ip_address(ip.strip())
            return f"{ip} is a valid IPv{addr.version} address"
        except ValueError:
            return f"{ip!r} is NOT a valid IP address"

    def _classify(self, ip: str) -> str:
        addr = self._parse_ip(ip)
        flags: list[str] = []
        if addr.is_private:
            flags.append("private")
        if addr.is_global:
            flags.append("public/global")
        if addr.is_loopback:
            flags.append("loopback")
        if addr.is_multicast:
            flags.append("multicast")
        if addr.is_reserved:
            flags.append("reserved")
        if addr.is_unspecified:
            flags.append("unspecified")
        if hasattr(addr, "is_link_local") and addr.is_link_local:
            flags.append("link-local")
        classification = ", ".join(flags) if flags else "unknown"
        return f"IPv{addr.version}  {ip}  →  {classification}"

    def _to_int(self, ip: str) -> str:
        addr = self._parse_ip(ip)
        return str(int(addr))

    def _from_int(self, number: int, ver: int) -> str:
        if ver == 6:
            return str(ipaddress.IPv6Address(number))
        return str(ipaddress.IPv4Address(number))

    def _network_info(self, net: str) -> str:
        n = self._parse_net(net)
        host_count = n.num_addresses - 2 if n.num_addresses > 2 else n.num_addresses
        return (
            f"Network   : {n.network_address}\n"
            f"Broadcast : {n.broadcast_address}\n"
            f"Netmask   : {n.netmask}\n"
            f"Prefix    : /{n.prefixlen}\n"
            f"Addresses : {n.num_addresses}\n"
            f"Usable    : {max(0, host_count)}"
        )

    def _hosts(self, net: str) -> str:
        n = self._parse_net(net)
        if n.num_addresses > 256:
            return f"Error: network too large ({n.num_addresses} addresses). Use a /24 or smaller."
        host_list = list(n.hosts())
        if not host_list:
            return f"No usable hosts in {net}"
        return "\n".join(str(h) for h in host_list)

    def _contains(self, net: str, ip: str) -> str:
        n = self._parse_net(net)
        addr = self._parse_ip(ip)
        inside = addr in n
        return f"{ip} {'IS' if inside else 'is NOT'} in {n}"

    def _supernet(self, net: str) -> str:
        n = self._parse_net(net)
        if n.prefixlen == 0:
            return "Error: already the most general network"
        return str(n.supernet())

    def _version(self, ip: str) -> str:
        addr = self._parse_ip(ip)
        return str(addr.version)

    def _expand_ipv6(self, ip: str) -> str:
        addr = self._parse_ip(ip)
        if not isinstance(addr, ipaddress.IPv6Address):
            return "Error: not an IPv6 address"
        return addr.exploded
