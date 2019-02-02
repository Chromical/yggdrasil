/*! @brief Flag for checking if YggInterface.hpp has already been included.*/
#ifndef YGGINTERFACE_HPP_
#define YGGINTERFACE_HPP_

#include "YggInterface.h"


/*!
  @brief C++ interface to yggInput_t functionality.

  The YggInput class is a basic wrapper around the C yggInput_t
  structure and associated functions from the YggInterface.h header.
  It provides the user with C++ style access to basic input via
  an IPC queue.
 */
class YggInput {
  yggInput_t _pi;
public:

  /*!
    @brief Constructor for YggInput.
    @param[in] name constant character pointer to name of input queue. This
    should be the argument to an input driver in the yaml specification file.
   */
  YggInput(const char *name) : _pi(yggInput(name)) {}

  /*! @brief Empty constructor for inheritance. */
  YggInput(yggInput_t x) : _pi(x) {}

  /*!
    @brief Constructor for YggInput with format.
    @param[in] name constant character pointer to name of input queue. This
    should be the argument to an input driver in the yaml specification file.
    @param[in] fmt character pointer to format string for parsing messages.
   */
  YggInput(const char *name, const char *fmt) : _pi(yggInputFmt(name, fmt)) {}

  /*!
    @brief Alias to allow freeing of underlying C struct at the class level.
  */
  void _destroy_pi() { ygg_free(&_pi); }
  
  /*!
    @brief Destructor for YggInput.
    See ygg_free in YggInterface.h for details.
  */
  ~YggInput() { _destroy_pi(); }
  
  /*!
    @brief Return the yggInput_t structure.
    @return yggInput_t structure underlying the class.
  */
  yggInput_t pi() {
    return _pi;
  };

  /*!
    @brief Receive a message shorter than YGG_MSG_MAX from the input queue.
    See ygg_recv in YggInterface.h for additional details.
    @param[out] data character pointer to allocated buffer where the message
    should be saved.
    @param[in] len size_t length of the allocated message buffer in bytes.
    @returns int -1 if message could not be received. Length of the received
    message if message was received.
   */
  int recv(char *data, const size_t len) { return ygg_recv(_pi, data, len); }

  /*!
    @brief Receive and parse a message shorter than YGG_MSG_MAX from the input
    queue. See yggRecv from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[out] ... mixed arguments that should be assigned parameters extracted
    using the format string. Since these will be assigned, they should be
    pointers to memory that has already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
   */
  int recv(const int nargs, ...) {
    size_t nargs_copy = (size_t)nargs;
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vcommRecv(_pi, 0, nargs_copy, va);
    va_end(va.va);
    return ret;
  }

  /*!
    @brief Receive and parse a message from the input queue, allowing destination
    variables to be reallocated. The pointers passed must be on heap.
    @param[in] nargs int Number of arguments being passed.
    @param[out] ... mixed arguments that should be assigned parameters extracted
    using the format string. Since these will be assigned, they should be
    pointers to memory that has already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
   */
  int recvRealloc(const int nargs, ...) {
    size_t nargs_copy = (size_t)nargs;
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vcommRecv(_pi, 1, nargs_copy, va);
    va_end(va.va);
    return ret;
  }
  
  /*!
    @brief Receive a message larger than YGG_MSG_MAX from the input queue.
    See ygg_recv_nolimit in YggInterface.h for additional details.
    @param[out] data character pointer to allocated buffer where the message
    should be saved.
    @param[in] len size_t length of the allocated message buffer in bytes.
    @returns int -1 if message could not be received. Length of the received
    message if message was received.
   */
  int recv_nolimit(char **data, const size_t len) {
    return ygg_recv_nolimit(_pi, data, len);
  }
  
  /*!
    @brief Receive and parse a message larger than YGG_MSG_MAX from the input
    queue. See yggRecv from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[out] ... mixed arguments that should be assigned parameters extracted
    using the format string. Since these will be assigned, they should be
    pointers to memory that has already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
   */
  int recv_nolimit(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vyggRecv(_pi, 0, nargs, va);
    va_end(va.va);
    return ret;
  }
  
};


/*!
  @brief C++ interface to yggOutput_t functionality.

  The YggOutput class is a basic wrapper around the C yggOutput_t
  structure and associated functions from the YggInterface.h header.
  It provides the user with C++ style access to basic output via
  an IPC queue.
 */
class YggOutput {
  yggOutput_t _pi;
public:
  
  /*!
    @brief Constructor for YggOutput.
    @param[in] name constant character pointer to name of output queue. This
    should be the argument to an output driver in the yaml specification file.
   */
  YggOutput(const char *name) : _pi(yggOutput(name)) {}
  
  /*!
    @brief Constructor for YggOutput with format.
    @param[in] name constant character pointer to name of output queue. This
    should be the argument to an output driver in the yaml specification file.
    @param[in] fmt character pointer to format string for formatting variables.
   */
  YggOutput(const char *name, const char *fmt) : _pi(yggOutputFmt(name, fmt)) {}

  /*! @brief Empty constructor for inheritance. */
  YggOutput(yggOutput_t x) : _pi(x) {}
  
  /*!
    @brief Alias to allow freeing of underlying C struct at the class level.
  */
  void _destroy_pi() { ygg_free(&_pi); }
  
  /*!
    @brief Destructor for YggOutput.
    See ygg_free in YggInterface.h for details.
  */
  ~YggOutput() { _destroy_pi(); }
  
  /*!
    @brief Return the yggOutput_t structure.
    @return yggOutput_t structure underlying the class.
  */
  yggOutput_t pi() {
    return _pi;
  };

  /*!
    @brief Send a message smaller than YGG_MSG_MAX to the output queue.
    If the message is larger than YGG_MSG_MAX an error code will be returned.
    See ygg_send in YggInterface.h for details.
    @param[in] data character pointer to message that should be sent.
    @param[in] len size_t length of message to be sent.
    @returns int 0 if send succesfull, -1 if send unsuccessful.
  */
  int send(const char *data, const size_t len) {
    return ygg_send(_pi, data, len);
  }

  /*!
    @brief Format and send a message smaller than YGG_MSG_MAX to the output
    queue. See yggSend from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[in] ... arguments for formatting.  
    @return integer specifying if the send was succesful. Values >= 0 indicate
    success.
  */
  int send(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vyggSend(_pi, nargs, va);
    va_end(va.va);
    return ret;
  }

  /*!
    @brief Send a message larger than YGG_MSG_MAX to the output queue.
    See ygg_send_nolimit in YggInterface.h for details.
    @param[in] data character pointer to message that should be sent.
    @param[in] len size_t length of message to be sent.
    @returns int 0 if send succesfull, -1 if send unsuccessful.
  */
  int send_nolimit(const char *data, const size_t len) {
    return ygg_send_nolimit(_pi, data, len);
  }
  
  /*!
    @brief Format and send a message larger than YGG_MSG_MAX to the output
    queue. See yggSend from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[in] ... arguments for formatting.  
    @return integer specifying if the send was succesful. Values >= 0 indicate
    success.
  */
  int send_nolimit(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vyggSend(_pi, nargs, va);
    va_end(va.va);
    return ret;
  }

  /*!
    @brief Send EOF message to output file, closing it.
    @returns int 0 if send was succesfull. All other values indicate errors.
   */
  int send_eof() { return ygg_send_eof(_pi); }
};
	

/*!
  @brief C++ interface to yggRpc_t functionality.

  The YggRpc class is a basic wrapper around the C yggRpc_t
  structure and associated functions from the YggInterface.h header.
  It provides the user with C++ style access to basic RPC messaging via IPC
  queues.
 */
class YggRpc {
  yggRpc_t _pi;
public:

  /*! @brief Empty constructor for inheritance. */
  YggRpc(yggRpc_t x) : _pi(x) {}
  
  /*!
    @brief Alias to allow freeing of underlying C struct at the class level.
  */
  void _destroy_pi() { ygg_free(&_pi); }
  
  /*!
    @brief Destructor for YggRpc.
    See ygg_free in YggInterface.h for details.
  */
  ~YggRpc() { _destroy_pi(); }
  
  /*!
    @brief Return the yggRpc_t structure.
    @return yggRpc_t structure underlying the class.
  */
  yggRpc_t pi() {
    return _pi;
  };

  /*!
    @brief Format and send a message to an RPC output queue.
    See rpcSend from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[in] ... arguments for formatting.  
    @return integer specifying if the send was succesful. Values >= 0 indicate
    success.
  */
  int send(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vrpcSend(_pi, nargs, va);
    va_end(va.va);
    return ret;
  }

  /*!
    @brief Receive and parse a message from an RPC input queue. 
    See rpcRecv from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[out] ... mixed arguments that should be assigned parameters extracted
    using the format string. Since these will be assigned, they should be
    pointers to memory that has already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
   */
  int recv(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vrpcRecv(_pi, nargs, va);
    va_end(va.va);
    return ret;
  }

  /*!
    @brief Receive and parse a message from an RPC input queue, allowing
    destination memory to be reallocated as necessary.
    See rpcRecv from YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[out] ... mixed arguments that should be assigned parameters extracted
    using the format string. Since these will be assigned and reallocated if
    they are not large enough, they should be references to pointer for heap
    memory that may or may not have already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
   */
  int recvRealloc(const int nargs, ...) {
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vrpcRecvRealloc(_pi, nargs, va);
    va_end(va.va);
    return ret;
  }
};


/*!
  @brief C++ interface to yggRpc_t server-side functionality.
  The YggRpcServer class is a basic wrapper around the C yggRpc_t
  structure and associated server-side functions from the YggInterface.h
  header. It provides the user with C++ style access to basic RPC server
  operations.
 */
class YggRpcServer : public YggRpc {
public:

  /*!
    @brief Constructor for YggRpcServer.
    @param[in] name constant character pointer name used for input and output
    queues.
    @param[in] inFormat character pointer to format that should be used for
    parsing input.
    @param[in] outFormat character pointer to format that should be used for
    formatting output.
   */
  YggRpcServer(const char *name, const char *inFormat, const char *outFormat) :
    YggRpc(yggRpcServer(name, inFormat, outFormat)) {}

  /*!
    @brief Destructor for YggRpcServer.
    See ygg_free in YggInterface.h for details.
  */
  ~YggRpcServer() { _destroy_pi(); }
  
};


/*!
  @brief C++ interface to yggRpc_t client-side functionality.
  The YggRpcClient class is a basic wrapper around the C yggRpc_t
  structure and associated client-side functions from the YggInterface.h
  header. It provides the user with C++ style access to basic RPC client
  operations.
 */
class YggRpcClient : public YggRpc {
public:

  /*!
    @brief Constructor for YggRpcClient.
    @param[in] name constant character pointer name used for input and output
    queues.
    @param[in] outFormat character pointer to format that should be used for
    formatting output.
    @param[in] inFormat character pointer to format that should be used for
    parsing input.
   */
  YggRpcClient(const char *name, const char *outFormat, const char *inFormat) :
    YggRpc(yggRpcClient(name, outFormat, inFormat)) {}

  /*!
    @brief Destructor for YggRpcClient.
    See ygg_free in YggInterface.h for details.
  */
  ~YggRpcClient() { _destroy_pi(); }
  
  /*!
    @brief Send request to an RPC server from the client and wait for a
    response, preserving the current sizes of memory at the provided output
    variable references.
    See rpcCall in YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[in,out] ... mixed arguments that include those that should be
    formatted using the output format string, followed by those that should be
    assigned parameters extracted using the input format string. These that will
    be assigned should be pointers to memory that has already been allocated.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
  */
  int call(const int nargs, ...) {
    yggRpc_t _cpi = pi();
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vrpcCall(_cpi, nargs, va);
    va_end(va.va);
    return ret;
  }
  
  /*!
    @brief Send request to an RPC server from the client and wait for a
    response, allowing the memory pointed to by the pointers that the output
    variables reference to be reallocated.
    See rpcCall in YggInterface.h for details.
    @param[in] nargs int Number of arguments being passed.
    @param[in,out] ... mixed arguments that include those that should be
    formatted using the output format string, followed by those that should be
    assigned parameters extracted using the input format string. These that will
    be assigned should be references to pointers for heap memory that may or may
    not have already been allocated. These will be reallocated if they are not
    large enough to receive data from the incoming message.
    @return integer specifying if the receive was succesful. Values >= 0
    indicate success.
  */
  int callRealloc(const int nargs, ...) {
    yggRpc_t _cpi = pi();
    va_list_t va;
    va_start(va.va, nargs);
    int ret = vrpcCallRealloc(_cpi, nargs, va);
    va_end(va.va);
    return ret;
  }
  
};


/*!
  @brief C++ interface to yggAsciiFileOutput_t functionality.
  The YggAsciiFileOutput class is a basic wrapper around the C
  yggAsciiFileOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file output operations.
 */
class YggAsciiFileOutput : public YggOutput {
public:

  /*!
    @brief Constructor for YggAsciiFileOutput.
    @param[in] name constant character pointer to the name of an output channel.
   */
  YggAsciiFileOutput(const char *name) :
    YggOutput(yggAsciiFileOutput(name)) {}
  
  /*! @brief Empty constructor for inheritance. */
  YggAsciiFileOutput(yggOutput_t x) :
    YggOutput(x) {}
  
  /*!
    @brief Send a single line to a file or queue.
    @param[in] line character pointer to line that should be sent.
    @returns int 0 if send was succesfull. All other values indicate errors.
   */
  int send_line(const char *line) { return send(line, strlen(line)); }

};


/*!
  @brief C++ interface to yggAsciiFileOutput_t functionality for local files.
  The YggAsciiFileOutput_local class is a basic wrapper around the C
  yggAsciiFileOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file output operations.
 */
class YggAsciiFileOutput_local : public YggAsciiFileOutput {
public:

  /*!
    @brief Constructor for YggAsciiFileOutput.
    @param[in] name constant character pointer to path of local file.
   */
  YggAsciiFileOutput_local(const char *name) :
    YggAsciiFileOutput(yggAsciiFileOutput_local(name)) {}
  
};


/*!
  @brief C++ interface to yggAsciiFileInput_t functionality.
  The YggAsciiFileInput class is a basic wrapper around the C
  yggAsciiFileInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file input operations.
 */
class YggAsciiFileInput : public YggInput {
public:

  /*!
    @brief Constructor for YggAsciiFileInput.
    @param[in] name constant character pointer to the name of an input channel.
   */
  YggAsciiFileInput(const char *name) :
    YggInput(yggAsciiFileInput(name)) {}

  /*! @brief Empty constructor for inheritance. */
  YggAsciiFileInput(yggInput_t x) :
    YggInput(x) {}
  
  /*!
    @brief Receive a single line from an associated file or queue.
    See af_recv_line in YggInterface.h for details.
    @param[out] line character pointer to allocate memory where the received
    line should be stored.
    @param[in] n size_t Size of the allocated memory block in bytes.
    @returns int Number of bytes read/received. Negative values indicate that
    there was either an error or the EOF message was received.
   */
  int recv_line(char *line, const size_t n) { return recv(line, n); }
  
};


/*!
  @brief C++ interface to yggAsciiFileInput_t functionality for local files.
  The YggAsciiFileInput_local class is a basic wrapper around the C
  yggAsciiFileInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file input operations.
 */
class YggAsciiFileInput_local : public YggAsciiFileInput {
public:

  /*!
    @brief Constructor for YggAsciiFileInput_local.
    @param[in] name constant character pointer to path of local file.
   */
  YggAsciiFileInput_local(const char *name) :
    YggAsciiFileInput(yggAsciiFileInput_local(name)) {}

};


/*!
  @brief C++ interface to yggAsciiTableOutput_t functionality.

  The YggAsciiTableOutput class is a basic wrapper around the C
  yggAsciiTableOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table output operations.
 */
class YggAsciiTableOutput : public YggAsciiFileOutput {
public:

  /*!
    @brief Constructor for YggAsciiTableOutput.
    @param[in] name constant character pointer to the name of an output channel.
    @param[in] format_str character pointer to format string that should be used
    to format rows into table lines.
   */
  YggAsciiTableOutput(const char *name, const char *format_str) :
    YggAsciiFileOutput(yggAsciiTableOutput(name, format_str)) {}

};


/*!
  @brief C++ interface to yggAsciiTableOutput_t functionality for local files.

  The YggAsciiTableOutput class is a basic wrapper around the C
  yggAsciiTableOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table output operations.
 */
class YggAsciiTableOutput_local : public YggAsciiFileOutput {
public:

  /*!
    @brief Constructor for YggAsciiTableOutput for local files.
    @param[in] name constant character pointer to path of local table.
    @param[in] format_str character pointer to format string that should be used
    to format rows into table lines.
   */
  YggAsciiTableOutput_local(const char *name, const char *format_str) :
    YggAsciiFileOutput(yggAsciiTableOutput_local(name, format_str)) {}

};


/*!
  @brief C++ interface to yggAsciiTableOutput_t functionality with arrays.

  The YggAsciiArrayOutput class is a basic wrapper around the C
  yggAsciiTableOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table output operations.
 */
class YggAsciiArrayOutput : public YggAsciiFileOutput {
public:

  /*!
    @brief Constructor for YggAsciiArrayOutput.
    @param[in] name constant character pointer to the name of an output channel.
    @param[in] format_str character pointer to format string that should be used
    to format arrays into a table.
   */
  YggAsciiArrayOutput(const char *name, const char *format_str) :
    YggAsciiFileOutput(yggAsciiArrayOutput(name, format_str)) {}

};


/*!
  @brief C++ interface to yggAsciiTableOutput_t functionality for local files.

  The YggAsciiArrayOutput class is a basic wrapper around the C
  yggAsciiTableOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table output operations.
 */
class YggAsciiArrayOutput_local : public YggAsciiFileOutput {
public:

  /*!
    @brief Constructor for YggAsciiArrayOutput for local files.
    @param[in] name constant character pointer to path of local table.
    @param[in] format_str character pointer to format string that should be used
    to format arrays into table columns.
   */
  YggAsciiArrayOutput_local(const char *name, const char *format_str) :
    YggAsciiFileOutput(yggAsciiArrayOutput_local(name, format_str)) {}

};


/*!
  @brief C++ interface to yggAsciiTableInput_t functionality.

  The YggAsciiTableInput class is a basic wrapper around the C
  yggAsciiTableInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table input operations.
 */
class YggAsciiTableInput : public YggAsciiFileInput {
public:

  /*!
    @brief Constructor for YggAsciiTableInput.
    Due to issues with the C++ version of vsscanf, flags and precision
    indicators for floating point format specifiers (e.g. %e, %f), must be
    removed so that table input can be properly parsed.
    @param[in] name constant character pointer to the name of an input channel.
   */
  YggAsciiTableInput(const char *name) :
    YggAsciiFileInput(yggAsciiTableInput(name)) {}

};

/*!
  @brief C++ interface to yggAsciiTableInput_t functionality for local files.

  The YggAsciiTableInput class is a basic wrapper around the C
  yggAsciiTableInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table input operations.
 */
class YggAsciiTableInput_local : public YggAsciiFileInput {
public:

  /*!
    @brief Constructor for YggAsciiTableInput_local.
    Due to issues with the C++ version of vsscanf, flags and precision
    indicators for floating point format specifiers (e.g. %e, %f), must be
    removed so that table input can be properly parsed.
    @param[in] name constant character pointer to path of local table.
   */
  YggAsciiTableInput_local(const char *name) :
    YggAsciiFileInput(yggAsciiTableInput_local(name)) {}

};

/*!
  @brief C++ interface to yggAsciiTableInput_t functionality for arrays.

  The YggAsciiArrayInput class is a basic wrapper around the C
  yggAsciiTableInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table input operations.
 */
class YggAsciiArrayInput : public YggAsciiFileInput {
public:

  /*!
    @brief Constructor for YggAsciiArrayInput.
    Due to issues with the C++ version of vsscanf, flags and precision
    indicators for floating point format specifiers (e.g. %e, %f), must be
    removed so that table input can be properly parsed.
    @param[in] name constant character pointer to the name of an input channel.
   */
  YggAsciiArrayInput(const char *name) :
    YggAsciiFileInput(yggAsciiArrayInput(name)) {}

};

/*!
  @brief C++ interface to yggAsciiTableInput_t functionality for local files
  as arrays.

  The YggAsciiArrayInput class is a basic wrapper around the C
  yggAsciiTableInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII table input operations.
 */
class YggAsciiArrayInput_local : public YggAsciiFileInput {
public:

  /*!
    @brief Constructor for YggAsciiArrayInput_local.
    Due to issues with the C++ version of vsscanf, flags and precision
    indicators for floating point format specifiers (e.g. %e, %f), must be
    removed so that table input can be properly parsed.
    @param[in] name constant character pointer to path of local table.
   */
  YggAsciiArrayInput_local(const char *name) :
    YggAsciiFileInput(yggAsciiArrayInput_local(name)) {}

};


/*!
  @brief C++ interface to yggPlyOutput_t functionality.
  The YggPlyOutput class is a basic wrapper around the C
  yggPlyOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file output operations.
 */
class YggPlyOutput : public YggOutput {
public:

  /*!
    @brief Constructor for YggPlyOutput.
    @param[in] name constant character pointer to the name of an output channel.
   */
  YggPlyOutput(const char *name) :
    YggOutput(yggPlyOutput(name)) {}
  
  /*! @brief Empty constructor for inheritance. */
  YggPlyOutput(yggOutput_t x) :
    YggOutput(x) {}
  
};


/*!
  @brief C++ interface to yggPlyInput_t functionality.
  The YggPlyInput class is a basic wrapper around the C
  yggPlyInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file input operations.
 */
class YggPlyInput : public YggInput {
public:

  /*!
    @brief Constructor for YggPlyInput.
    @param[in] name constant character pointer to the name of an input channel.
   */
  YggPlyInput(const char *name) :
    YggInput(yggPlyInput(name)) {}

  /*! @brief Empty constructor for inheritance. */
  YggPlyInput(yggInput_t x) :
    YggInput(x) {}
  
};


/*!
  @brief C++ interface to yggObjOutput_t functionality.
  The YggObjOutput class is a basic wrapper around the C
  yggObjOutput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file output operations.
 */
class YggObjOutput : public YggOutput {
public:

  /*!
    @brief Constructor for YggObjOutput.
    @param[in] name constant character pointer to the name of an output channel.
   */
  YggObjOutput(const char *name) :
    YggOutput(yggObjOutput(name)) {}
  
  /*! @brief Empty constructor for inheritance. */
  YggObjOutput(yggOutput_t x) :
    YggOutput(x) {}
  
};


/*!
  @brief C++ interface to yggObjInput_t functionality.
  The YggObjInput class is a basic wrapper around the C
  yggObjInput_t structure and associated functions from the
  YggInterface.h header. It provides the user with C++ style access to basic
  ASCII file input operations.
 */
class YggObjInput : public YggInput {
public:

  /*!
    @brief Constructor for YggObjInput.
    @param[in] name constant character pointer to the name of an input channel.
   */
  YggObjInput(const char *name) :
    YggInput(yggObjInput(name)) {}

  /*! @brief Empty constructor for inheritance. */
  YggObjInput(yggInput_t x) :
    YggInput(x) {}
  
};


#endif /*YGGINTERFACE_HPP_*/