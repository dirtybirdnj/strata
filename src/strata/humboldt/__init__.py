"""
strata.humboldt: Geometric transformation and spatial analysis.

"Nature considered rationally, that is to say, submitted to the process of
thought, is a unity in diversity of phenomena; a harmony, blending together
all created things, however dissimilar in form and attributes."
    — Alexander von Humboldt, Cosmos

The most important aim of all cartographic processing is this: to recognize
unity in diversity—to comprehend all the single features as revealed by our
data sources, to judge single geometries separately without surrendering
their bulk, and to grasp the landscape's essence under the cover of outer
appearances.

When we subtract water from land, we do not merely perform a geometric
operation. We reveal the true relationship between these phenomena—the way
the lake carves its space from the surrounding towns, the way the island
asserts its separation from the mainland. These are not merely shapes but
connections made visible.

Functions:
    subtract() - Remove geometry of one feature from another
    clip() - Keep only geometry within bounds
    merge() - Combine multiple features into one
    simplify() - Reduce geometry complexity
    identify_islands() - Find land masses enclosed by water
    buffer() - Expand or contract geometry
    transform_crs() - Project between coordinate systems
"""

# TODO: Implement geometry operations
