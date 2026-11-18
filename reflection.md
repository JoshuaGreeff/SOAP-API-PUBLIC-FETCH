# Reflection

I began by choosing the InterSystems SOAP Demonstration Service from the provided public WSDL list. I used Zeep to read the WSDL and call its `AddInteger` operation, then placed that client call behind small Flask GET and POST routes. The routes collect two numbers, validate that they are whole numbers between -10,000 and 10,000, and return a JSON response that includes the SOAP result.

One surprise was that I did not need to manually write a SOAP XML envelope. Zeep reads the WSDL and creates the Python method from the service contract, while `serialize_object()` helps convert the SOAP response into normal Python data for Flask. The project evolved from a direct client call into a small service with reusable validation and custom error messages. I understand better how a WSDL describes the operation a client can call and how SOAP faults differ from normal validation errors. I would like to learn more about handling more complex nested SOAP responses.
