from typing import Any #Allows flexible type hints
#New change
#Harmless comment
#Testing feature branch change 
import httpx2 #sends HTTP requests to the weather API
from mcp.server import MCPServer #Imports the MCP server class

mcp = MCPServer("weather") #Creates the weather MCP server

NWS_API_BASE = "https://api.weather.gov" #Base URL of the US weather API
USER_AGENT = "weather-app/1.0" #Identifies our application

async def make_nws_request(url: str) -> dict[str, Any] | None:  #Helper Functions: Request data from weather API
    """Make a request to the NWS API with proper error handling """
    headers = {"User-Agent": USER_AGENT, #Identifies our application
               "Accept": "application/geo+json"}#Requests GeoJSON data
    async with httpx2.AsyncClient() as client: #Creates an HTTP client
        try:
            response = await client.get(url, headers=headers, timeout=30.0) #Sends the request
            response.raise_for_status() #Check for HTTP errors
            return response.json()#Converts JSON into Python data
        except Exception:
            return None #Returns None if the request fails

#Formats an alert into readable text
def format_alert(feature: dict)-> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"] #Gets alert details
    return f"""
Event: {props.get("event","Unknown")}
Area:{props.get("areaDesc", "Unknown")}
Severity:{props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instructions", "No specific instructions provided")}
"""

#MCP tool: retrieves active alerts for a US state
#Implementing tool execution
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get active weather alerts for a US STATE.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """

    url=f"{NWS_API_BASE}/alerts/active/area/{state}" #Builds API URL
    data = await make_nws_request(url) #Fetches alert data

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state"

    alerts = [format_alert(feature) for feature in data["features"]]  #Formats each alert
    return "\n---\n".join(alerts) #Combines alerts into one response

#MCP tool: retrieves a forecast using coordinates
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args: 
        latitude: Latitude of the location
        longitude: Longitude of location
    """

    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}" #Builds location
    points_data = await make_nws_request(points_url) #Gets location metadata

    if not points_data:
        return "Unable to fetch forecast data for this location."

    forecast_url = points_data["properties"]["forecast"] #Gets forecast URL
    forecast_data = await make_nws_request(forecast_url) #Fetches forecast

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    periods = forecast_data["properties"]["periods"] #Gets forecast periods
    forecasts = [] #Stores formatted forecasts
    for period in periods[:5]: #Processes first five forecasts
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast) #Adds forecast to the list
    return "\n---\n".join(forecasts) #Returns combined forecasts

#Starts the MCP server using STDIO communication
#Initialise & run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")

#Helloo
#Another change 
