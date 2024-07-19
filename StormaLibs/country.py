from config import FLAG_UNK

__all__ = (
    "flag",
    "FLAG_UNK"
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
        "ZAF": "🇿🇦"
    }


def flag(n) -> str:
    return '🇪🇺' if n in ('MAI', 'MASTER', 'DB') else COUNTRYFLAGS_Names.get(n[:3], FLAG_UNK)
