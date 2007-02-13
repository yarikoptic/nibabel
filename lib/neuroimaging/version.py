version = '0.1.2'
release=False


def _get_svn_version(svn_doc):
    for node in svn_doc.childNodes:
         if hasattr(node, 'getAttribute'):
             rev = node.getAttribute('revision')
             if rev is not None:
                 return rev.encode('ascii')


if not release:
    import sys
    import os
    from xml.dom.minidom import parse
    import neuroimaging

    nipy = sys.modules.get('neuroimaging')
    try:
        svn_entries = os.path.join(os.path.dirname(nipy.__file__),'.svn', 'entries')
        svn_doc = parse(open(svn_entries)).documentElement
        svn_version = _get_svn_version(svn_doc)

        version += '.dev'+svn_version
    except IOError:
        version += '.dev'+'_unknown_svn'