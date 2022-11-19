Part II: How PyFLP works
========================

    💡 You should read Part I before this.

PyFLP's entry-point :meth:`pyflp.parse` verifies the headers and parses all the
events. These events are collected into an :class:`pyflp._events.EventTree`.

Schematic diagram
-----------------

.. svgbob::
   :align: center

    ┌──────────────────────────────────────────────────────────────────────────┐
    │     Events - binary representation - low level API - Stage 1 parser      │
    │                                                                          │
    │ ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────┐  │
    │ │  Project-wide / 1-time  │ │      Per-instance       │ │    Shared   │  │
    │ │┌─────────┐   ┌─────────┐│ │┌─────────┐   ┌─────────┐│ │ ┌─────────┐ │  │
    │ ││ Event 1 │   │ Event 2 ││ ││ Event 3 │   │ Event 4 ││ │ │ Event 5 │ │  │
    │ ││ id: 199 │ → │ id: 159 ││→││ id: 64  │ → │ id: 215 ││→│ │ id: 225 │ │  │
    │ ││ string  │   │ integer ││ ││ integer │   │ struct  ││ │ │   AoS   │ │  │
    │ │└─────────┘   └─────────┘│ │└─────────┘   └─────────┘│ │ └─────────┘ │  │
    │ └─────│──────────────│────┘ └──────│────────────│─────┘ └──────│──────┘  │
    │       └──┬───────────╯╭────────────┴────────────╯              │         │
    │ ┌───────────────┐ ┌───────┬──────────┬──────────────┐ ┌────────────────┐ │
    │ │    Model A    │ │ Model │ Model B1 │ attr_64: int │ │ Model C1: e[0] │ │
    │ │ attr_199: str │ │ list  ├──────────┼──────────────┤ ├────────────────┤ │
    │ │ attr_159: int │ │ of B  │ Model B2 │ attr_215: X  │ │ Model C2: e[1] │ │
    │ └───────────────┘ └───────┴──────────┴──────────────┘ └────────────────┘ │
    │                                                                          │
    │    Models - PyFLP's representation - high level API - Stage 2 parser     │
    └──────────────────────────────────────────────────────────────────────────┘

PyFLP provides a high-level and a low-level API. Normally the high-level API
should get your work done. However, it might be possible that due to a bug or
super old versions of FLPs the high level API fails to parse. In that case,
one can use the low-level API. Using it requires a deeper understanding of
the FLP format and how the GUI hierarchies relate to their underlying events.

What it does?
-------------

In a nutshell, PyFLP parses the events and creates a better semantic structure
from it (as shown in the above diagram; stage 2 parser). I call this a "model".

.. _architecture-model:

Model
-----

A model acts like a "view" or alternate representation of the event data. It
has no state of its own and its composed of descriptors which get and set
values from the events directly. A model is essentially stateless.

This has some advantages as compared to stateful models:

1. The underlying event data and the values returned from the model descriptors
   *i.e. its attributes or properties* always remain in sync with each other.
2. Since modifying the event data at a binary level means conforming to the
   various size and range limits imposed by C's data types, it can act as basic
   validation for no extra cost or implementation.
3. Avoid the use of private members in the models itself. Private members maybe
   a good idea in languages which have better implementation of such concepts,
   but in Python its quite as good as shooting yourself in the foot. Due to
   Python's do-whatever-you-want nature, it can lead to some very bad coding
   practices. This is one of the big reasons why PyFLP underwent a rewrite.
4. Nothing is done in class constructor, so if a particular set of events are
   out of order or follow a sequence not yet understood by PyFLP, they will
   fail only for the attributes which use them. Hence, what is *parseable* can
   still be parsed. This lazy evaluation can be good and bad both, but with
   adequate unit tests its more good than it is bad.

Creating a model involves a good amount of reverse engineering and insight. The
models PyFLP has are based as close to the GUI objects inside FL Studio. For
e.g. a pattern is represented by :class:`pyflp.pattern.Pattern`.

A model is constructed with events it requires and additional information (like
PPQ) its descriptors might need.

Disadvantages
-------------

Difficult to make ports
^^^^^^^^^^^^^^^^^^^^^^^

The current working of PyFLP is non-replicable in most other languages.
Descriptors are a Python specific feature I have yet to find anywhere else.
Therefore, the possibility of a port that's as clean (and featured) as PyFLP is
less. Most languages however have some sort of 3rd party Python interop library
available, so its not like PyFLP is completely unuseable from other languages.

A quick search on Github will return some FLP parsers available for other
languages, but almost all of them are pretty much unmaintained or archived.

Unit-testing is paramount
^^^^^^^^^^^^^^^^^^^^^^^^^

Due to the lazy nature of models and their descriptors, each of them should be
tested so as to ensure that no changes in the event handling affect or break.

For a long time, I used only a single FLP to test all of PyFLP's API. Things
have changed now and I use presets exported from FL Studio itself for the
testing of a huge chunk of API to ensure isolation of test results.

The problem is that all the test data comes from FL Studio itself and can
be only really validated in the same. That's the reason I usually don't
raise any errors event if I know quite surely that, for example a value out of
range is set for some property.
