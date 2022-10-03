# OTP Gen
_A multi-language interface generator for interacting with OTP (Online-Theme-Park) clusters_

_For more information on the DC/OTP system, see the official [Panda3D Docs](https://docs.panda3d.org/1.10/python/programming/networking/distributed/index)_

One of the major drawbacks of the DC (Distributed Class) system is the requirement to parse a .dc file at runtime.
Implementing a runtime parser comes with many challenges, especially in environments where shipping a .dc file or using
runtime reflection is not possible or practical.

*OTP Gen* aims to solve this problem by pre-parsing .dc file(s) at build-time, and outputting both interfaces and utility
classes directly into your projects source tree. This also has the added benefit of somewhat obfuscating fields, as 
keywords are not included in the output (although you should never rely on security through obscurity.)

*OTP Gen* is still early in development, and as such there may be some small bugs and incomplete typings.
Please open an issue if you encounter any of these.

## Supported Languages ##

- TypeScript (_development_)
- C#/Unity (_planned_)

## Limitations ##

In environments where runtime reflection is not possible, developers will need to manually register class implementations
within OTPClientRepository.

*OTP Gen* is designed to interface with the **original** OTP server message types/order.
Support for [Astron](https://github.com/Astron/Astron) is planned for the future.
In the meantime, you can override OTPClientRepository in your source.

## License ##

*OTP Gen* is licensed under the "MIT License" for more info, refer to the [LICENSE](LICENSE.md) file.
