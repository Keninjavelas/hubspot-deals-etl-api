from typing import Iterator, Dict, Any
# Changed from '.hubspot_api_service' to 'services.hubspot_api_service'
from services.hubspot_api_services import HubSpotApiService
import os

class HubSpotDataSource:
    def __init__(self, api_service: HubSpotApiService):
        self.api_service = api_service
        # Defines the properties to fetch from the HubSpot API
        self.properties = "dealname,amount,pipeline,dealstage,createdate,hs_lastmodifieddate,closedate,deal_owner_id"

    def get_all_deals(self, checkpoint_after: str = None) -> Iterator[Dict[str, Any]]:
        """
        Extracts all deals from the HubSpot API, handling pagination.
        It uses a generator to yield a page of data at a time.
        `checkpoint_after` allows resuming an extraction from a specific record.
        """
        after = checkpoint_after
        has_more = True
        
        while has_more:
            try:
                response = self.api_service.get_deals(properties=self.properties, after=after)
                
                # Check if the API returned any results
                if not response.get("results"):
                    has_more = False
                    continue

                # Yield the page of results
                yield response["results"]
                
                # Check for more data to paginate
                paging = response.get("paging")
                if paging and "next" in paging:
                    after = paging["next"]["after"]
                else:
                    has_more = False
            except Exception as e:
                # Log the error but re-raise it to halt the process
                print(f"Error during data extraction: {e}")
                raise