def get_page_from_context(ctx, component_id):
    """
    Extract page number from Dash callback context for a specific component.

    Args:
        ctx: Dash callback context
        component_id: String identifier to match in the prop_id (e.g., 'make-popularity')

    Returns:
        int: Page number if found, otherwise 1 (default)
    """
    if not ctx.triggered:
        return 1

    triggered_info = ctx.triggered[0]
    if component_id in triggered_info['prop_id']:
        return triggered_info['value']['page']
    else:
        return 1
