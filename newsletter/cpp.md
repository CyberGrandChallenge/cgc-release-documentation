# CGC News Letter 2

## Introduction

The C++ Programming Language provides interesting opportunities to
generate challenge binaries. Many C++ features such as function or
operator overloading are completely lost in statically linked,
stripped binaries, but the heavy use of pointers and function pointers
demonstrate the challenges inherent in complex object oriented
applications.

## Background

The Cyber Grand Challenge FAQ [[1]][ref1], Answer #12 states that the
"The C family of languages" will be used to write CBs.  This newsletter
addresses some of the caveats of producing challenge binaries with C++
(specifically the supported clang++ compiler in the reference virtual
machine).

## Implementation

Several features of the C++ language can be made to work with minimal
effort.  Features like abstract classes (vtables), function / operator
overloads, auto variables, etc. work without effort; those features
requiring special handling are detailed below.

### `new` / `delete`

The `new` and `delete` operators can be implemented in terms of
`malloc()`/`free()` if available in the CB's library (ultimately in
terms of the `allocate()` and `deallocate()` DECREE system calls).

    void *operator new(unsigned int sz) {
      return malloc(sz);
    }

    void *operator new[](unsigned int sz) {
      return ::operator new(sz);
    }

    void operator delete(void *p) {
      free(p);
    }

    void operator delete[](void *p) {
      ::operator delete(p);
    }

### Static constructors

The libcgc runtime does not automatically call static constructors: it
simply calls `main()` followed by `_terminate()`. Static constructors are
given entries in a hidden linker array bounded by the symbols
`__init_array_start` and `__init_array_end`.  The functions are simply
called in order of appearance in the array, like so:

    #define __hidden __attribute__((__visibility__("hidden")))
    
    void *__dso_handle; /* required symbol, but not used */
    
    extern "C" {
      extern void (*__init_array_start[])(int, char **, char **) __hidden;
      extern void (*__init_array_end[])(int, char **, char **) __hidden;
    };
    
    void call_inits(void) {
      size_t asize;
      void (*fn)(int, char **, char **);
  
      asize = __init_array_end - __init_array_start;
      for (size_t n = 0; n < asize; n++) {
        fn = __init_array_start[n];
        if (fn && (long)fn != 1)
          fn(0, (char **)NULL, (char **)NULL);
      }
    }
    
    int main() {
      call_inits();
      ...
    }

### Static destructors

The compiler generates calls to a function called `__cxa_atexit()` for
static destructors.  CB authors must provide an implementation of that
function (it is indirectly called from a `__init_array` function, so
support for static constructors must be in place first). A possible
implementation of `__cxa_atexit` is show below.

    extern "C" {
      int __cxa_atexit(void (*func)(void *), void *arg, void *dso);
    };

    static struct exit_handlers {
      void (*func)(void *);
      void *arg;
    } exit_handlers[100];
    static int nhandlers = 0;
    
    int __cxa_atexit(void (*func)(void *), void *arg, void *dso) {
      if (nhandlers == sizeof(exit_handlers)/sizeof(exit_handlers[0]))
        return (-1);
      exit_handlers[nhandlers].func = func;
      exit_handlers[nhandlers].arg = arg;
      nhandlers++;
      return (0);
    }

    int main() {
    
      ...
    
      for (int i = 0; i < nhandlers; i++)
        exit_handlers[i].func(exit_handlers[i].arg);
      return (0);
    }

### Miscellaneous

CB Authors may, under some circumstances, need to provide
implementations of the following functions:

    void std::terminate(void);
    extern "C" {
      void *memset(void *, int, size_t);
      void __cxa_pure_virtual();
    };

## Caveats

Several language features are notably missing.  The Standard Template
Library (STL) is not provided for challenge binaries. This includes
most of the C++ runtime (iostreams, maps, vectors, etc.). CB authors
are not allowed to reuse existing code but are allowed to write their own
libraries for reuse (see [[3]][ref3] for further guidance).

C++ exceptions are currently not implemented and doing so appears to be
non-trivial exercise. Some of the necessary functionality is present
in libcgc in the form of `setjmp`/`longjmp`.  CB authors requiring
exceptions will have to provide an implementations of:

    __cxa_call_unexpected();
    void *__cxa_begin_catch(void *);
    _Unwind_Resume();
    /* possibly more [[2]][ref2] */

Run Time Type Information (RTTI) is also not supported. This
effectively disables `dynamic_cast<>` and `typeid`. Support for this
language feature requires the implementation of various objects
conforming to the CLANG C++ ABI version 1, e.g.:

    __cxxabiv1::__class_type_info
    __cxxabiv1::__si_class_type_info
    etc.
	   
An example implementation can be found in the CLANG C++ Runtime library.

## Example

An example challenge binary using C++ can be found in [[4]][ref4]. It uses all
of the features described above to implement a virtual pet
service. The cgc-cb.mk Makefile assumes that C++ files are named with
a ".cc" extension and will call the compiler appropriately.

## Conclusion

The examples provided here demonstrate the use of C++ as a challenge
binary source language with the starting for a CB author to implement some of
the richer C++ features.

## References

[1] [Cyber Grant Challenge: Frequently Asked Questions(FAQ)][ref1]

[ref1]: https://cgc.darpa.mil/documents.aspx "Cyber Grand Challenge: Frequently Asked Questions (FAQ), July 24, 2014."

[2] [libc++ ABI Specification][ref2]

[ref2]: http://libcxxabi.llvm.org/spec.html "libc++ ABI Specification"

[3] [Submitting a Challenge Binary][ref3]

[ref3]: https://github.com/CyberGrandChallenge/cgc-release-documentation/blob/master/walk-throughs/submitting-a-cb.md "Submitting a Challenge Binary"

[4] [TNETS_00002 in reference virtual machine][ref4]

[ref4]: file:///usr/share/cgc-sample-challenges/examples/TNETS_00002 "TNETS_00002 in reference virtual machine"
