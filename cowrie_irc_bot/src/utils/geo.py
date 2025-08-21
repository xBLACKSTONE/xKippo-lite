"""
Geolocation utilities for IP addresses.
"""
import logging
from typing import Dict, Any, Optional, Tuple


class GeoLocator:
    """Geolocate IP addresses."""

    def __init__(self):
        """Initialize the geolocation service."""
        self.logger = logging.getLogger("cowrie_irc_bot.geo")
        self.geo_db = None
        
    def load_database(self) -> bool:
        """
        Load the geolocation database.
        
        Returns:
            True if database loaded successfully, False otherwise
        """
        try:
            # Try to import geoip2 (optional dependency)
            import geoip2.database
            import geoip2.errors
            
            # Try to load MaxMind database (default location)
            try:
                db_path = "/usr/share/GeoIP/GeoLite2-City.mmdb"
                self.geo_db = geoip2.database.Reader(db_path)
                return True
            except FileNotFoundError:
                # Try alternate location
                try:
                    db_path = "/var/lib/GeoIP/GeoLite2-City.mmdb"
                    self.geo_db = geoip2.database.Reader(db_path)
                    return True
                except FileNotFoundError:
                    self.logger.warning("GeoIP database not found. Geolocation will be disabled.")
                    return False
            except Exception as e:
                self.logger.error(f"Error loading GeoIP database: {e}")
                return False
                
        except ImportError:
            self.logger.warning("geoip2 module not installed. Geolocation will be disabled.")
            return False
            
    def get_location(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Get geolocation information for an IP address.
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Dictionary containing geolocation information, or None if not available
        """
        if not self.geo_db:
            if not self.load_database():
                return None
                
        try:
            # Skip private IPs
            if ip_address.startswith(('10.', '192.168.', '172.16.', '127.', '169.254.')):
                return None
                
            response = self.geo_db.city(ip_address)
            
            return {
                "country_code": response.country.iso_code,
                "country_name": response.country.name,
                "city": response.city.name,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
            }
            
        except Exception as e:
            self.logger.debug(f"Error geolocating IP {ip_address}: {e}")
            return None
            
    def get_location_string(self, ip_address: str) -> str:
        """
        Get a formatted string with geolocation information.
        
        Args:
            ip_address: IP address to geolocate
            
        Returns:
            Formatted string with geolocation information
        """
        location = self.get_location(ip_address)
        if not location:
            return "unknown location"
            
        city = location.get("city", "")
        country = location.get("country_name", "")
        country_code = location.get("country_code", "")
        
        if city and country:
            return f"{city}, {country} ({country_code})"
        elif country:
            return f"{country} ({country_code})"
        else:
            return "unknown location"