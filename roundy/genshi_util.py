class DocType(object):
    """Defines a number of commonly used DOCTYPE declarations as constants."""

    HTML_STRICT = (
        'html', '-//W3C//DTD HTML 4.01//EN',
        'http://www.w3.org/TR/html4/strict.dtd'
    )
    HTML_TRANSITIONAL = (
        'html', '-//W3C//DTD HTML 4.01 Transitional//EN',
        'http://www.w3.org/TR/html4/loose.dtd'
    )
    HTML_FRAMESET = (
        'html', '-//W3C//DTD HTML 4.01 Frameset//EN',
        'http://www.w3.org/TR/html4/frameset.dtd'
    )
    HTML = HTML_STRICT

    HTML5 = ('html', None, None)

    XHTML_STRICT = (
        'html', '-//W3C//DTD XHTML 1.0 Strict//EN',
        'http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd'
    )
    XHTML_TRANSITIONAL = (
        'html', '-//W3C//DTD XHTML 1.0 Transitional//EN',
        'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'
    )
    XHTML_FRAMESET = (
        'html', '-//W3C//DTD XHTML 1.0 Frameset//EN',
        'http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd'
    )
    XHTML = XHTML_STRICT

    XHTML11 = (
        'html', '-//W3C//DTD XHTML 1.1//EN',
        'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd'
    )

    SVG_FULL = (
        'svg', '-//W3C//DTD SVG 1.1//EN',
        'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'
    )
    SVG_BASIC = (
        'svg', '-//W3C//DTD SVG Basic 1.1//EN',
        'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11-basic.dtd'
    )
    SVG_TINY = (
        'svg', '-//W3C//DTD SVG Tiny 1.1//EN',
        'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11-tiny.dtd'
    )
    SVG = SVG_FULL

    @classmethod
    def get(cls, name):
        """Return the ``(name, pubid, sysid)`` tuple of the ``DOCTYPE``
        declaration for the specified name.
        
        The following names are recognized in this version:
         * "html" or "html-strict" for the HTML 4.01 strict DTD
         * "html-transitional" for the HTML 4.01 transitional DTD
         * "html-frameset" for the HTML 4.01 frameset DTD
         * "html5" for the ``DOCTYPE`` proposed for HTML5
         * "xhtml" or "xhtml-strict" for the XHTML 1.0 strict DTD
         * "xhtml-transitional" for the XHTML 1.0 transitional DTD
         * "xhtml-frameset" for the XHTML 1.0 frameset DTD
         * "xhtml11" for the XHTML 1.1 DTD
         * "svg" or "svg-full" for the SVG 1.1 DTD
         * "svg-basic" for the SVG Basic 1.1 DTD
         * "svg-tiny" for the SVG Tiny 1.1 DTD
        
        :param name: the name of the ``DOCTYPE``
        :return: the ``(name, pubid, sysid)`` tuple for the requested
                 ``DOCTYPE``, or ``None`` if the name is not recognized
        :since: version 0.4.1
        """
        return {
            'html': cls.HTML, 'html-strict': cls.HTML_STRICT,
            'html-transitional': DocType.HTML_TRANSITIONAL,
            'html-frameset': DocType.HTML_FRAMESET,
            'html5': cls.HTML5,
            'xhtml': cls.XHTML, 'xhtml-strict': cls.XHTML_STRICT,
            'xhtml-transitional': cls.XHTML_TRANSITIONAL,
            'xhtml-frameset': cls.XHTML_FRAMESET,
            'xhtml11': cls.XHTML11,
            'svg': cls.SVG, 'svg-full': cls.SVG_FULL,
            'svg-basic': cls.SVG_BASIC,
            'svg-tiny': cls.SVG_TINY
        }.get(name.lower())
