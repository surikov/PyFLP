📚 Handbook
============

This page contains some ideas on how one can use PyFLP for automating
tasks (*to a certain extent*) which can only be done via FL Studio.

A basic-to-intermediate level of Python knowledge is assumed.

*These all are written from a dev's POV. I would ♥ to get more ideas and hear
about different use cases.*

📦 Exporting an FLP to a ZIP
-----------------------------

Imagine you had a folder structure like this:

.. code-block::

   📁 Samples
      ├─── 🥁 kick.wav
      ├─── 👏 clap.wav
      └─── 🎵 toms.wav
   📄 MyGreatSong.flp


    For the purpose of simplicity, assume that ``📄 MyGreatSong.flp`` uses only
    the samples from ``📁 Samples`` and all **sample file names are unique**.

The code below will create a ZIP containing all the samples used

.. code-block:: python

   from zipfile import ZipFile
   import pyflp

   project = pyflp.parse("MyGreatSong.flp")

   with ZipFile("MyGreatSong.zip", "x") as zp:
       zp.write("MyGreatSong.flp")

       for sampler in project.channels.samplers:
           if sampler.sample_path is not None:
               zp.write(sampler.sample_path)

.. caution:: Missing samples

   The above code assumes that all the samples exist at the paths the FLP has
   stored. If any of the samples aren't found, there will be an error.

   FL Studio doesn't give up this easily. It searches up a lot of paths,
   including but not limited to the recursive scanning of folders which are:

   - Current directory.
   - Added to the sample browser.
   - Containing previous samples / missing samples.

This will create a ZIP file of the structure:

.. code-block::

   📦 MyGreatSong.zip
      ├─── 📄 MyGreatSong.flp
      ├─── 🥁 kick.wav
      ├─── 👏 clap.wav
      └─── 🎵 toms.wav

.. hint:: FL Studio stock samples

   While this will work for 3rd party samples *unless there's 2 samples with
   the same name*, FL Studio doesn't store the full path inside an FLP for
   stock samples. See :attr:`pyflp.channel.Sampler.sample_path` for more info.

🔓 Unlocking FLPs saved with a demo version of FL Studio
---------------------------------------------------------

.. seealso::

   :attr:`Project.licensed <pyflp.project.Project.licensed>` and
   :attr:`_PluginBase.demo_mode <pyflp.plugin._PluginBase.demo_mode>`.

.. code-block:: python

   import pyflp

   project = pyflp.parse("/path/to/myflp.flp")

   # Unlock the FLP itself
   project.registered = True

   # Unlock trial version native plugins
   for instument in project.channels.instruments:
       instrument.demo_mode = False

   for insert in project.mixer:
       for slot in insert:
           if slot.plugin is not None:
              slot.plugin.demo_mode = False
