import abc

from builtins import object
from future.utils import listitems, with_metaclass


class DocStringInheritor(type):
    """
    A variation on
    http://groups.google.com/group/comp.lang.python/msg/26f7b4fcb4d66c95
    by Paul McGuire
    """

    def __new__(meta, name, bases, clsdict):
        if not ("__doc__" in clsdict and clsdict["__doc__"]):
            for mro_cls in (mro_cls for base in bases for mro_cls in base.mro()):
                doc = mro_cls.__doc__
                if doc:
                    clsdict["__doc__"] = doc
                    break
        for attr, attribute in listitems(clsdict):
            if not attribute.__doc__:
                for mro_cls in (mro_cls for base in bases for mro_cls in base.mro() if hasattr(mro_cls, attr)):
                    doc = getattr(getattr(mro_cls, attr), "__doc__")
                    if doc:
                        if isinstance(attribute, property):
                            clsdict[attr] = property(attribute.fget, attribute.fset, attribute.fdel, doc)
                        else:
                            attribute.__doc__ = doc
                        break
        return type.__new__(meta, name, bases, clsdict)


# DocStringInheritor is the metaclass in python 2 and 3
class IFuzzable(with_metaclass(DocStringInheritor, object)):
    """Describes a fuzzable message element or message.

    The core functionality on which boofuzz runs:

    1. mutations() -- iterate mutations.
    2. mutant_index, mutate(), render(), reset() are an older interface used to simulate mutations().
    3. render() returns either the normal value or the currently-being-mutated value.
    3. name() -- gets the specific element's name; may be replaced in the future.
    4. fuzzable() -- indicates whether an element should be fuzzed. This used to be checked externally, but is now
                     checked within mutations()
    5. original_value() -- used to get the default value of the element.
    6. num_mutations() -- Number of mutations that an element yields.
    7. __len__() -- an element should describe its own size when rendered.
    8. __repr__() -- for nice readable user interfaces
    9. __nonzero__() -- Allows one to use `if someFuzzableObject` to check for null. Questionable practice.

    The mutation and original_value functions are the most fundamental.

    """

    name_counter = 0

    @property
    def fuzzable(self):
        """If False, this element should not be mutated in normal fuzzing."""
        return self._fuzzable


    @abc.abstractproperty
    def mutations(self):
        """Yields mutations."""
        return

    @property
    def mutant_index(self):
        """Index of current mutation. 0 => normal value. 1 => first mutation.
        """
        return

    @property
    @abc.abstractmethod
    def original_value(self):
        """Original, non-mutated value of element."""
        return

    @property
    def name(self):
        """Element name, should be specific for each instance."""
        if self._name is None:
            IFuzzable.name_counter += 1
            self._name = "{0}{1}".format(type(self).__name__, IFuzzable.name_counter)
        return self._name

    @property
    def qualified_name(self):
        if not hasattr(self, '_context_path'):
            self._context_path = None
        return ".".join(filter(None, (self._context_path, self.name)))

    @property
    def context_path(self):
        return self._context_path

    @context_path.setter
    def context_path(self, x):
        self._context_path = x

    def mutate(self):
        """Mutate this element. Returns True each time and False on completion.

        Use reset() after completing mutations to bring back to original state.

        Mutated values available through render().

        Returns:
            bool: True if there are mutations left, False otherwise.
        """
        return

    @abc.abstractmethod
    def num_mutations(self):
        """Return the total number of mutations for this element.

        Returns:
            int: Number of mutated forms this primitive can take
        """
        return

    @abc.abstractmethod
    def render(self):
        """Return rendered value. Equal to original value after reset().
        """
        return

    def encode(self, value, child_data):
        return value

    def render_mutated(self, mutation):
        """Render after applying mutation, if applicable."""
        child_data = self.get_child_data(mutation=mutation)
        if self.qualified_name in mutation.mutations:
            return self.encode(mutation.mutations[self.qualified_name], child_data=child_data)
            #return self.encode(value=value, child_data=child_data)
        else:
            #return self.encode_value(self.original_value)
            return self.encode(value=self.original_value, child_data=child_data)

    def get_child_data(self, mutation):
        return None

    def reset(self):
        """Reset element to pre-mutation state."""
        return

    @abc.abstractmethod
    def __repr__(self):
        return

    @abc.abstractmethod
    def __len__(self):
        """Length of field. May vary if mutate() changes the length.

        Returns:
            int: Length of element (length of mutated element if mutated).
        """
        return

    @abc.abstractmethod
    def __bool__(self):
        """Make sure instances evaluate to True even if __len__ is zero.

        Design Note: Exists in case some wise guy uses `if my_element:` to
        check for null value.

        Returns:
            bool: True
        """
        return
