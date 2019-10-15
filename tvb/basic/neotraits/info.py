"""
Functions that inform a user about the state of a traited class or object.

Some of these functions are here so that they won't clutter the core trait implementation.
"""

import numpy
import typing


def auto_docstring(cls):
    """ generate a docstring for the new class in which the Attrs are documented """
    header = 'Traited class [{}.{}]'.format(cls.__module__, cls.__name__)

    doc = [
        header,
        len(header) * '^',
        '',
        'Attributes declared',
        '"""""""""""""""""""',
        ''
    ]
    # a rst definition list for all attributes
    for attr_name in cls.declarative_attrs:
        attr = getattr(cls, attr_name)
        # the standard repr of the attribute
        doc.append('{} : {}'.format(attr_name, str(attr)))
        # and now the doc property
        for line in attr.doc.splitlines():
            doc.append('    ' + line.lstrip())
        doc.append('')

    if cls.declarative_props:
        doc.extend([
            '',
            'Properties declared',
            '"""""""""""""""""""',
            ''
        ])

    for prop_name in cls.declarative_props:
        prop = getattr(cls, prop_name)
        # the standard repr
        doc.append('  {} : {}'.format(prop_name, str(prop)))
        # now fish the docstrings
        for line in prop.attr.doc.splitlines():
            doc.append('    ' + line.lstrip())
        if prop.fget.__doc__ is not None:
            for line in prop.fget.__doc__.splitlines():
                doc.append('    ' + line.lstrip())

    doc = '\n'.join(doc)

    if cls.__doc__ is not None:
        return cls.__doc__ + doc
    else:
        return doc


def narray_summary_info(ar, ar_name='', omit_shape=False):
    # type: (numpy.ndarray, str, bool) -> typing.Dict[str, str]
    """
    A 2 column table represented as a dict of str->str
    """
    if ar is None:
        return {'is None': 'True'}

    ret = {}
    if not omit_shape:
        ret.update({
            'shape': str(ar.shape),
            'dtype': str(ar.dtype),
        })

    if ar.size == 0:
        ret['is empty'] = 'True'
        return ret

    if ar.dtype.kind in 'iufc':
        has_nan = numpy.isnan(ar).any()
        if has_nan:
            ret['has NaN'] = 'True'
        ret['[min, median, max]'] = '[{:g}, {:g}, {:g}]'.format(ar.min(), numpy.median(ar), ar.max())

    if ar_name:
        return {ar_name + ' ' + k: v for k, v in ret.iteritems()}
    else:
        return ret


def narray_describe(ar):
    # type: (numpy.ndarray) -> str
    summary = narray_summary_info(ar)
    ret = []
    for k in sorted(summary):
        ret.append('{:<12}{}'.format(k, summary[k]))
    return '\n'.join(ret)


# these are here and not on HasTraits just so that that class is not
# complicated by irrelevant string formatting

def trait_object_str(self):
    cls = type(self)
    summary = self.summary_info()
    result = ['{} ('.format(cls.__name__)]
    maxlenk = max(len(k) for k in summary)

    for k in sorted(summary):
        result.append('  {:.<{}} {}'.format(k + ' ', maxlenk, summary[k]))
    result.append(')')
    return '\n'.join(result)


def trait_object_repr_html(self):
    cls = type(self)
    result = [
        '<table>',
        '<h3>{}</h3>'.format(cls.__name__),
        '<thead><tr><th></th><th style="text-align:left;width:40%">value</th></tr></thead>',
        '<tbody>']

    summary = self.summary_info()

    for k in sorted(summary):
        row_fmt = '<tr><td>{}</td><td style="text-align:left;"><pre>{}</pre></td>'
        result.append(row_fmt.format(k, summary[k]))

    result += ['</tbody></table>']

    return '\n'.join(result)
