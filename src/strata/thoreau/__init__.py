"""
strata.thoreau: Data acquisition from authoritative sources.

"I fathomed it easily with a cod-line and a stone weighing about a pound
and a half, and could tell accurately when the stone left the bottom,
by having to pull so much harder before the water got underneath to help me."
    — Henry David Thoreau, Walden

I have walked to the Census Bureau, so to speak, and returned with their
TIGER files—those careful delineations of every county, town, and water body
in the nation. It is remarkable how many will speculate about boundaries
without taking the trouble to fetch the authoritative source.

The work of acquisition is simple but requires patience. One must know where
to look—the Census for American boundaries, CanVec for Canadian waters,
Quebec's open data for their municipalities. Each source has its own character,
its own way of organizing what it knows.

Functions:
    fetch() - Acquire data from a source URI
    fetch_census() - Acquire US Census TIGER data
    fetch_canvec() - Acquire Canadian CanVec data
    fetch_quebec() - Acquire Quebec Open Data
    validate_source() - Verify the integrity of acquired data
"""

# TODO: Implement data acquisition functions
