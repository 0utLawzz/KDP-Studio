"""Measured text-boundary validation shared by PDF generators."""

from __future__ import annotations


class TextBoundsError(ValueError):
    """Raised when measured text crosses a configured safe boundary."""

    def __init__(self, label, overflow, left_overflow, right_overflow):
        self.label = label
        self.overflow = overflow
        self.left_overflow = left_overflow
        self.right_overflow = right_overflow
        super().__init__(
            f"{label} overflows the safe bounds by {overflow:.2f}pt "
            f"(left {left_overflow:.2f}pt, right {right_overflow:.2f}pt)"
        )


def validate_text_bounds(c, text, font, size, cx_or_x, safe_left, safe_right, label):
    """Raise when measured text crosses the supplied horizontal safe bounds.

    Numeric positions are treated as centered x coordinates.  Left- and
    right-aligned text can pass ``("left", x)`` or ``("right", x)`` as the
    ``cx_or_x`` value respectively.
    """
    if safe_left > safe_right:
        raise ValueError(
            f"{label} has invalid safe bounds: "
            f"left {safe_left:.2f}pt is greater than right {safe_right:.2f}pt"
        )

    anchor = "center"
    coordinate = cx_or_x
    if isinstance(cx_or_x, tuple):
        if len(cx_or_x) != 2 or cx_or_x[0] not in {"left", "center", "right"}:
            raise ValueError(
                f"{label} has an invalid text anchor: {cx_or_x!r}"
            )
        anchor, coordinate = cx_or_x

    width = c.stringWidth(text, font, size)
    if anchor == "left":
        text_left = coordinate
        text_right = coordinate + width
    elif anchor == "right":
        text_left = coordinate - width
        text_right = coordinate
    else:
        text_left = coordinate - width / 2
        text_right = coordinate + width / 2

    left_overflow = max(0.0, safe_left - text_left)
    right_overflow = max(0.0, text_right - safe_right)
    overflow = max(left_overflow, right_overflow)
    if overflow > 0:
        raise TextBoundsError(
            label,
            overflow,
            left_overflow,
            right_overflow,
        )


def draw_safe_string(c, text, font, size, x, y, safe_left, safe_right, label):
    """Validate and draw a left-aligned string."""
    validate_text_bounds(
        c, text, font, size, ("left", x), safe_left, safe_right, label
    )
    c.drawString(x, y, text)


def draw_safe_centered_string(
    c, text, font, size, cx, y, safe_left, safe_right, label
):
    """Validate and draw a centered string."""
    validate_text_bounds(c, text, font, size, cx, safe_left, safe_right, label)
    c.drawCentredString(cx, y, text)


def draw_safe_right_string(c, text, font, size, x, y, safe_left, safe_right, label):
    """Validate and draw a right-aligned string."""
    validate_text_bounds(
        c, text, font, size, ("right", x), safe_left, safe_right, label
    )
    c.drawRightString(x, y, text)