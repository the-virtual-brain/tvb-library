# -*- coding: utf-8 -*-

# Data structure manipulations and conversions
from six import string_types
import numpy as np
from collections import OrderedDict
from tvb.basic.logger.builder import get_logger

LOG = get_logger(__name__)

def is_numeric(value):
    return isinstance(value, (float, np.float, np.float64, np.float32, np.float16, np.float128,
                              int, np.int, np.int0, np.int8, np.int16, np.int32, np.int64,
                              complex, np.complex, np.complex64, np.complex128, np.complex256, np.long, np.number))


def is_integer(value):
    return isinstance(value, (int, np.int, np.int0, np.int8, np.int16, np.int32, np.int64))


def isequal_string(a, b, case_sensitive=False):
    if case_sensitive:
        return a == b
    else:
        try:
            return a.lower() == b.lower()
        except AttributeError:
            LOG.warning("Case sensitive comparison!")
            return a == b


def obj_to_dict(obj):
    """
    :param obj: Python object to introspect
    :return: dictionary after recursively taking obj fields and their values
    """
    if obj is None:
        return obj
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, (np.float32,)):
        return float(obj)
    if isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    if isinstance(obj, list):
        ret = []
        for val in obj:
            ret.append(obj_to_dict(val))
        return ret
    ret = {}
    for key in obj.__dict__:
        val = getattr(obj, key, None)
        ret[key] = obj_to_dict(val)
    return ret


def sort_dict(d):
    return OrderedDict(sorted(d.items(), key=lambda t: t[0]))


def list_of_dicts_to_dicts_of_ndarrays(lst, shape=None):
    d = dict(list(zip(lst[0], list(zip(*list([d.values() for d in lst]))))))
    if isinstance(shape, tuple):
        for key, val in d.items():
            d[key] = np.reshape(np.stack(d[key]), shape)
    else:
        for key, val in d.items():
            d[key] = np.stack(d[key])
            for sh in d[key].shape[:0:-1]:
                if sh == 1:
                    d[key] = np.squeeze(d[key], axis=-1)
                else:
                    break
    return d


def ensure_list(arg):
    if not (isinstance(arg, list)):
        try:  # if iterable
            if isinstance(arg, (string_types, dict)):
                arg = [arg]
            elif hasattr(arg, "__iter__"):
                arg = list(arg)
            else:  # if not iterable
                arg = [arg]
        except:  # if not iterable
            arg = [arg]
    return arg


def flatten_list(lin, sort=False):
    lout = []
    for sublist in lin:
        if isinstance(sublist, (list, tuple)):
            temp = flatten_list(list(sublist))
        else:
            temp = [sublist]
        for item in temp:
            lout.append(item)
    if sort:
        lout.sort()
    return lout


def get_list_or_tuple_item_safely(obj, key):
    try:
        return obj[int(key)]
    except:
        return None


def find_labels_inds(labels, keys, modefun="find", two_way_search=False, break_after=np.iinfo(np.int64).max):
    if isequal_string(modefun, "equal"):
        modefun = lambda x, y: isequal_string(x, y)
    else:
        if two_way_search:
            modefun = lambda x, y: (x.find(y) >= 0) or (y.find(x) >= 0)
        else:
            modefun = lambda x, y: x.find(y) >= 0
    inds = []
    keys = ensure_list(keys)
    labels = ensure_list(labels)
    counts = 0
    for key in keys:
        for label in labels:
            if modefun(label, key):
                inds.append(labels.index(label))
                counts += 1
            if counts >= break_after:
                return inds
    return inds


def generate_region_labels(n_regions, labels=[], str=". ", numbering=True, numbers=[]):
    if len(numbers) != n_regions:
        numbers = list(range(n_regions))
    if len(labels) == n_regions:
        if numbering:
            return np.array([str.join(["%d", "%s"]) % tuple(l) for l in zip(numbers, labels)])
        else:
            return np.array(labels)
    else:
        return np.array(["%d" % l for l in numbers])


# This function is meant to confirm that two objects assumingly of the same type are equal, i.e., identical
def assert_equal_objects(obj1, obj2, attributes_dict=None, logger=None):
    def print_not_equal_message(attr, field1, field2, logger):
        # logger.error("\n\nValueError: Original and read object field "+ attr + " not equal!")
        # raise_value_error("\n\nOriginal and read object field " + attr + " not equal!")
        LOG.warning("Original and read object field " + attr + " not equal!" +
                "\nOriginal field:\n" + str(field1) +
                "\nRead object field:\n" + str(field2), logger)

    if isinstance(obj1, dict):
        get_field1 = lambda obj, key: obj[key]
        if not (isinstance(attributes_dict, dict)):
            attributes_dict = dict()
            for key in obj1.keys():
                attributes_dict.update({key: key})
    elif isinstance(obj1, (list, tuple)):
        get_field1 = lambda obj, key: get_list_or_tuple_item_safely(obj, key)
        indices = list(range(len(obj1)))
        attributes_dict = dict(list(zip([str(ind) for ind in indices], indices)))
    else:
        get_field1 = lambda obj, attribute: getattr(obj, attribute)
        if not (isinstance(attributes_dict, dict)):
            attributes_dict = dict()
            for key in obj1.__dict__.keys():
                attributes_dict.update({key: key})
    if isinstance(obj2, dict):
        get_field2 = lambda obj, key: obj.get(key, None)
    elif isinstance(obj2, (list, tuple)):
        get_field2 = lambda obj, key: get_list_or_tuple_item_safely(obj, key)
    else:
        get_field2 = lambda obj, attribute: getattr(obj, attribute, None)

    equal = True
    for attribute in attributes_dict:
        # print attributes_dict[attribute]
        field1 = get_field1(obj1, attributes_dict[attribute])
        field2 = get_field2(obj2, attributes_dict[attribute])
        try:
            # TODO: a better hack for the stupid case of an ndarray of a string, such as model.zmode or pmode
            # For non numeric types
            if isinstance(field1, string_types) or isinstance(field1, list) or isinstance(field1, dict) \
                    or (isinstance(field1, np.ndarray) and field1.dtype.kind in 'OSU'):
                if np.any(field1 != field2):
                    print_not_equal_message(attributes_dict[attribute], field1, field2, logger)
                    equal = False
            # For numeric numpy arrays:
            elif isinstance(field1, np.ndarray) and not field1.dtype.kind in 'OSU':
                # TODO: handle better accuracy differences, empty matrices and complex numbers...
                if field1.shape != field2.shape:
                    print_not_equal_message(attributes_dict[attribute], field1, field2, logger)
                    equal = False
                elif np.any(np.float32(field1) - np.float32(field2) > 0):
                    print_not_equal_message(attributes_dict[attribute], field1, field2, logger)
                    equal = False
            # For numeric scalar types
            elif is_numeric(field1):
                if np.float32(field1) - np.float32(field2) > 0:
                    print_not_equal_message(attributes_dict[attribute], field1, field2, logger)
                    equal = False
            else:
                equal = assert_equal_objects(field1, field2, logger=logger)
        except:
            try:
                LOG.warning("Comparing str(objects) for field "
                        + str(attributes_dict[attribute]) + " because there was an error!", logger)
                if np.any(str(field1) != str(field2)):
                    print_not_equal_message(attributes_dict[attribute], field1, field2, logger)
                    equal = False
            except:
                LOG.error("ValueError: Something went wrong when trying to compare "
                                  + str(attributes_dict[attribute]) + " !", logger)

    if equal:
        return True
    else:
        return False


def shape_to_size(shape):
    shape = np.array(shape)
    shape = shape[shape > 0]
    return np.int(np.max([shape.prod(), 1]))
