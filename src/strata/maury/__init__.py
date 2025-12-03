"""
strata.maury: Pipeline orchestration and layer composition.

"There is a river in the ocean. In the severest droughts it never fails,
and in the mightiest floods it never overflows. Its banks and its bottom
are of cold water, while its current is of warm."
    — Matthew Fontaine Maury, The Physical Geography of the Sea

I have been consulting the records of many sources—the Census Bureau's
careful delineations, the Canadian government's water features, Quebec's
municipal boundaries—and the results, when properly combined, are remarkable.

No single source tells the complete story. The Census knows American waters
but not Canadian. Quebec knows its municipalities but not the lake that spans
the border. Only by aggregating these observations, by establishing a uniform
system of processing, can we produce charts worthy of the landscape they
represent.

There is a river in the data. It flows from acquisition through transformation
to visualization. In the severest complexity it never fails, and in the
mightiest datasets it never overflows—provided we respect the proper order
of operations.

The layer sandwich is our chart of charts: backgrounds at bottom, major water
bodies above, towns with their cutouts next, small water to show through,
and highways at the very top.

Classes:
    Recipe - Parse and validate .strata.yaml files
    Pipeline - Execute the build process
    LayerStack - Manage layer ordering and composition
"""

from strata.maury.recipe import Recipe

__all__ = ["Recipe"]
