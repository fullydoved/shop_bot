"""Tool checkout services."""

from django.utils import timezone
from .models import Tool, Checkout


def add_tool(name: str, description: str = '', location: str = '', category: str = '') -> Tool:
    """Add a new tool to the system.

    Args:
        name: Tool name
        description: Optional description
        location: Where the tool normally lives
        category: Tool category

    Returns:
        Created Tool instance
    """
    tool, created = Tool.objects.get_or_create(
        name__iexact=name,
        defaults={
            'name': name,
            'description': description,
            'location': location,
            'category': category,
        }
    )

    if not created:
        # Update existing tool
        if description:
            tool.description = description
        if location:
            tool.location = location
        if category:
            tool.category = category
        tool.save()

    return tool


def remove_tool(name: str) -> bool:
    """Remove a tool from the system.

    Args:
        name: Tool name (partial match)

    Returns:
        True if removed, False if not found
    """
    tool = Tool.objects.filter(name__icontains=name).first()
    if tool:
        tool.delete()
        return True
    return False


def checkout_tool(tool_name: str, borrower: str, notes: str = '') -> tuple[Checkout | None, str]:
    """Check out a tool.

    Args:
        tool_name: Tool name (partial match)
        borrower: Name of person borrowing
        notes: Optional notes

    Returns:
        Tuple of (Checkout instance or None, status message)
    """
    tool = Tool.objects.filter(name__icontains=tool_name).first()
    if not tool:
        return None, f"Tool '{tool_name}' not found"

    if not tool.is_available:
        current = tool.current_checkout
        return None, f"{tool.name} is already checked out to {current.borrower} ({current.duration})"

    checkout = Checkout.objects.create(
        tool=tool,
        borrower=borrower,
        notes=notes,
    )

    return checkout, f"{tool.name} checked out to {borrower}"


def return_tool(tool_name: str) -> tuple[Checkout | None, str]:
    """Return a checked-out tool.

    Args:
        tool_name: Tool name (partial match)

    Returns:
        Tuple of (Checkout instance or None, status message)
    """
    tool = Tool.objects.filter(name__icontains=tool_name).first()
    if not tool:
        return None, f"Tool '{tool_name}' not found"

    checkout = tool.current_checkout
    if not checkout:
        return None, f"{tool.name} is not checked out"

    checkout.returned_at = timezone.now()
    checkout.save()

    return checkout, f"{tool.name} returned (was out for {checkout.duration})"


def find_tool(query: str) -> list[Tool]:
    """Find tools matching a query.

    Args:
        query: Search term

    Returns:
        List of matching tools
    """
    return list(Tool.objects.filter(name__icontains=query))


def list_tools(available_only: bool = False, checked_out_only: bool = False) -> list[Tool]:
    """List all tools.

    Args:
        available_only: Only show available tools
        checked_out_only: Only show checked out tools

    Returns:
        List of tools
    """
    tools = Tool.objects.all()

    if available_only:
        # Filter to tools with no active checkouts
        tools = tools.exclude(checkouts__returned_at__isnull=True)
    elif checked_out_only:
        # Filter to tools with active checkouts
        tools = tools.filter(checkouts__returned_at__isnull=True).distinct()

    return list(tools)


def get_borrower_tools(borrower: str) -> list[Checkout]:
    """Get all tools currently checked out to a borrower.

    Args:
        borrower: Borrower name (partial match)

    Returns:
        List of active checkouts
    """
    return list(
        Checkout.objects.filter(
            borrower__icontains=borrower,
            returned_at__isnull=True
        ).select_related('tool')
    )


def get_checkout_history(tool_name: str = None, limit: int = 10) -> list[Checkout]:
    """Get checkout history.

    Args:
        tool_name: Optional tool name to filter by
        limit: Max number of records

    Returns:
        List of checkouts
    """
    queryset = Checkout.objects.select_related('tool')

    if tool_name:
        queryset = queryset.filter(tool__name__icontains=tool_name)

    return list(queryset[:limit])
