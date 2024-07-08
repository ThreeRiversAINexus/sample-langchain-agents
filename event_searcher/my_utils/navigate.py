# This is a subclass of the NavigateTool class from the langchain_community package.
# I needed to add exception handling to the _arun method, so I subclassed it and overrode the method.
# I also added a print statement to the method to see if it was being called.
# Otherwise, if you get a 404 error, the program will crash.


from typing import TYPE_CHECKING, Annotated, Literal, Optional
from langchain_community.tools.playwright.navigate import NavigateTool
from langchain_community.tools.playwright.base import lazy_import_playwright_browsers, BaseBrowserTool 
if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.sync_api import Browser as SyncBrowser
else:
    try:
        # We do this so pydantic can resolve the types when instantiating
        from playwright.async_api import Browser as AsyncBrowser
        from playwright.sync_api import Browser as SyncBrowser
    except ImportError:
        pass
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
class NexusNavigateTool(NavigateTool):
    @classmethod
    def from_browser(
        cls,
        sync_browser: Optional[SyncBrowser] = None,
        async_browser: Optional[AsyncBrowser] = None,
    ) -> BaseBrowserTool:
        """Instantiate the tool."""
        lazy_import_playwright_browsers()
        return cls(async_browser=async_browser, handle_tool_error="There was a problem navigating to the site. The site is inaccessible.", handle_validation_error="There was a problem when reading the site. The site is inaccessible.")

    async def _arun(
        self,
        url: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        # Call parent class method
        try:
            return await super()._arun(url, run_manager)
        except Exception as e:
            print("Inside NexusNavigateTool.arun")
            return str(e)

    # We need to wrap this with exception handling
    #     async def _arun(
    #       self,
    #       url: str,
    #       run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    #        str:
    #       """Use the tool."""
    #       if self.async_browser is None:
    #           raise ValueError(f"Asynchronous browser not provided to {self.name}")
    #       page = await aget_current_page(self.async_browser)
    #       response = await page.goto(url)
    #       status = response.status if response else "unknown"
    #       return f"Navigating to {url} returned status code {status}"
    # but pass through the valueerror and catch everything else,
    # returning an error message about how the website was inaccessible