# sre-interview-prep

The first part of this list contains resources that are good cramming material for SRE/Devops interviews. These resources actually work pretty well for 75% of the SRE/Devops interviews that you may face. For the other 25% (more selective companies), they require a deeper understanding that requires structured learning of fundamentals. For example, lets say they ask "describe the Linux booting process". Several of the resources below e.g., `linux-sys-admin`, `random` will give a cursory overview of the steps involved, but if the interviewer starts digging into a particular step e.g., with BIOS you will be lost without fundamental knowledge of computer architecture and assembly. Similar examples can be provided for other questions regarding application performance, memory management, CPU scheduling, etc.

# Good Cramming Material

- `algoexpert`
    * Contains problems solved in algoexpert stored in Jupyter Notebooks
- `google-sre`
    * Contains notes from Google's Site Reliability Engineering [books](https://landing.google.com/sre/books/)
- `lfs`
    * Contains notes and scripts from [Linux from Scratch](http://www.linuxfromscratch.org/)
- `linux-sys-admin`
    * Contains notes from [Linux System Adminstration Handbook](https://www.amazon.com/UNIX-Linux-System-Administration-Handbook/dp/0134277554/ref=sr_1_8?dchild=1&keywords=linux&qid=1592369959&sr=8-8)
- `past`
    * Contains past interview questions related to parsing and other sys admin tasks
- `random`
    * `fb-resource-*.md` contains notes from two study resources that Facebook provided for Production Engineer systems interview
    * `google-foobar.ipynb` contains questions from the Google Foobar hiring challenge
    * `troubleshooting.md` contains notes from Brendan Gregg's [USE](http://www.brendangregg.com/usemethod.html) and [TSA](http://www.brendangregg.com/tsamethod.html) methods for troubleshooting
    * `what-happens-google.md` contains notes on the classic "What happens when you type google.com into your browser"
- `tech-blogs`
    * Contains notes on tech blogs of various companies

# Fundamental Material
What I realized after completing the above is that there are knowledge gaps that require structured learning. For example, to fully understand the Linux boot process, you need to understand assembly code as well as computer architecture. The same for various concepts e.g., memory management, CPU scheduling, etc.

- `kernel`
    * Contains notes about the Linux Kernel from [here](https://github.com/0xAX/linux-insides)