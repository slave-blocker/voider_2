# voider_2

ssh passwords are replaced by keys.

Being able to forward ports on your router makes you a senator.
If you are not a senator then you are a citizen.
No need for static ip addresses, .onion addresses are used as the 
anchors.

the patch on the wire was improved.

Use the phone GXP1610 .

other interoperable phones are still being searched. 

Symmetric encryption of the udp packets, for the udp holepunch should still be done.



Independently from the phonecalls a more generic vpn network could be tried.
Under this model perhaps it is possible to redirect the default gateway within a limit
of 3 hops. This means a transitive vpn network. Therefore within a network namespace there would be 2 default gateways.
One going into the tun0 and one coming out of the tun0.
So if Alice -> Bob and Bob -> John, then Alice (->) John .
Here -> means "connects to" or "is client of".
Here (->) means that John would receive the traffic from Alice and recognize that its coming from two hops away.
It could also be that : John -> Jane . Then Alice [->] Jane .
Here [->] means that Jane would receive the traffic of Alice passing over Bob then over John, and since its 3 hops away 
Jane would force it out on its connection to the internet.

Furthermore this could be randomized every half an hour, at every hop.
Ongoing tcp connections would be dropped and would need to restart.

A small gui is given...
