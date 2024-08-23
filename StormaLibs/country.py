from config import FLAG_UNK

__all__ = (
    "COUNTRYFLAGS_Names",
    "MASTER_SERVERS",
    "flag"
)

COUNTRYFLAGS_Names = {
    'NLD': '🇳🇱',
    'FRA': '🇫🇷',
    'GER': '🇩🇪',
    'RUS': '🇷🇺',
    'CHI': '🇨🇱',
    'MEX': '🇲🇽',
    'PER': '🇵🇪',
    'USA': '🇺🇸',
    'SOU': '🇿🇦',
    'CHN': '🇨🇳',
    'KOR': '🇰🇷',
    'CAN': '🇨🇦',
    'BRA': '🇧🇷',
    'AUS': '🇦🇺',
    'IND': '🇮🇳',
    'JAP': '🇯🇵',
    'SIN': '🇸🇬',
    'POL': '🇵🇱',
    'IRN': '🇮🇷',
    'UAE': '🇦🇪',
    'TUR': '🇹🇷',
    'ARG': '🇦🇷',
    'COL': '🇨🇴',
    'CRI': '🇨🇷',
    'TAI': '🇹🇼',
    'SAU': '🇸🇦',
    "UKR": "🇺🇦",
    "CHL": "🇨🇱",
    "ZAF": "🇿🇦",
    "BAH": "🇧🇭"
}
MASTER_SERVERS = {
    "MASTER": '🇪🇺',
    "MASTER2": '🇨🇳',
    "DB": '🇪🇺',
    "MAI": '🇪🇺',
}


def flag(n) -> str:
    s = MASTER_SERVERS.get(n)
    return s if s is not None else COUNTRYFLAGS_Names.get(n[:3], FLAG_UNK)
