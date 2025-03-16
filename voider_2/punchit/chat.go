package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"time"
	//    "strconv"
	//        "strings"

	"github.com/libp2p/go-libp2p"
	"github.com/libp2p/go-libp2p/core/crypto"
	"github.com/libp2p/go-libp2p/core/host"
	"github.com/libp2p/go-libp2p/core/network"
	"github.com/libp2p/go-libp2p/core/peer"
	"github.com/libp2p/go-libp2p/core/protocol"
	drouting "github.com/libp2p/go-libp2p/p2p/discovery/routing"
	dutil "github.com/libp2p/go-libp2p/p2p/discovery/util"

	dht "github.com/libp2p/go-libp2p-kad-dht"
	//ma "github.com/multiformats/go-multiaddr"
	"github.com/ipfs/go-log/v2"
	rcmgr "github.com/libp2p/go-libp2p/p2p/host/resource-manager"
)

var peeridloaded = []string{}

var logger = log.Logger("rendezvous")

func writedatasafu(rw *bufio.ReadWriter) {
	defer func() {
		if err := recover(); err != nil {
			logger.Info("writeData panic")
		}
	}()
	writeData(rw)
}

func randInt(min, max int) int {
	return min + rand.Intn(max-min)
}

func handleStream(stream network.Stream) {
	logger.Info("Got a new stream!", stream.Conn().RemotePeer())
	logger.Info("Got a new stream! : ", stream.Conn().RemoteMultiaddr())

	s2 := stream.Conn().RemotePeer().String()
	s3 := stream.Conn().RemoteMultiaddr().String()

	if contains(peeridloaded, s2) {
		fmt.Println("Got a stream to : ", s2, " writing id and address to file.")
		time.Sleep(10 * time.Second)
		os.WriteFile("peerid_to_connect", []byte(s2), 0666)
		os.WriteFile("peer_addr", []byte(s3), 0666)
	} else {
		stream.Close()
	}
}

func readData(rw *bufio.ReadWriter) {
	for {
		str, err := rw.ReadString('\n')
		if err != nil {
			fmt.Println("Error reading from buffer")
			panic(err)
		}

		if str == "" {
			return
		}
		if str != "\n" {
			// Green console colour: 	\x1b[32m
			// Reset console colour: 	\x1b[0m
			fmt.Printf("\x1b[32m%s\x1b[0m> ", str)
		}

	}
}

func writeData(rw *bufio.ReadWriter) {
	stdReader := bufio.NewReader(os.Stdin)

	for {
		fmt.Print("> ")
		sendData, err := stdReader.ReadString('\n')
		if err != nil {
			fmt.Println("Error reading from stdin")
			panic(err)
		}

		_, err = rw.WriteString(fmt.Sprintf("%s\n", sendData))
		if err != nil {
			fmt.Println("Error writing to buffer")
			panic(err)
		}
		err = rw.Flush()
		if err != nil {
			fmt.Println("Error flushing buffer")
			panic(err)
		}
	}
}

func search_and_connect(ctx context.Context, host host.Host, myPeer string, routingDiscovery *drouting.RoutingDiscovery, config Config) {

	var peerid_to_connect peer.ID

	logger.Info("oioioi...")

	peerChan, err := routingDiscovery.FindPeers(ctx, myPeer)
	if err != nil {
		panic(err)
	}

	logger.Info("popopo...")

	for peer := range peerChan {
		if peer.ID == host.ID() {
			continue
		}
		logger.Info("Found peer:", peer)
		logger.Info("Found peer.ID:", peer.ID)

		logger.Info("Connecting to:", peer)

		s1 := myPeer
		s2 := peer.ID.String()

		if s1 == s2 {
			peerid_to_connect = peer.ID
			goto punching
		} else {
			continue
		}
	}

	select {}

punching:
	logger.Info("start to punch to id : ", peerid_to_connect)

	os.WriteFile("punching", []byte("punching"), 0666)

	for k := 0; k < 10; k++ {
		logger.Info("Round : ", k)

		stream, err := host.NewStream(ctx, peerid_to_connect, protocol.ID(config.ProtocolID))

		if err != nil {
			logger.Warning("Connection failed: !!!ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ!!!!!!!!!!!!!!! ", err)
			time.Sleep(60 * time.Second)
			continue
		} else {
			rw := bufio.NewReadWriter(bufio.NewReader(stream), bufio.NewWriter(stream))
			//time.Sleep(1 * time.Second)
			//go writeData(rw)
			go writedatasafu(rw)
			go readData(rw)
			logger.Info("Connected to:", stream.Conn().RemoteMultiaddr())

			logger.Info(peerid_to_connect.String(), "Mfer!")

			time.Sleep(10 * time.Second)

			os.WriteFile("peerid_to_connect", []byte(peerid_to_connect.String()), 0666)
			os.WriteFile("peer_addr", []byte(stream.Conn().RemoteMultiaddr().String()), 0666)
		}
	}
}

func tunnel_down(client bool, idx int) bool {

    var j int
    var str string

	if client {

		file, err := os.Open("../clients/occupants")
		if err != nil {
			fmt.Println("../clients/occupants Err()")
		}

		scanner := bufio.NewScanner(file)
		// optionally, resize scanner's capacity for lines over 64K, see next example

		j = 1
		for scanner.Scan() {
			str = scanner.Text()
			//fmt.Println(str)
			if j == idx {
				if str != "4" {
					logger.Info("str ", str)
					file.Close()
					return true
				}
			}
			j++
		}

		if err := scanner.Err(); err != nil {
			fmt.Println("scanner.Err()")
		}

		file.Close()
		return false
	} else {
		file, err := os.Open("../servers/occupants")
		if err != nil {
			fmt.Println("../servers/occupants Err()")
		}

		scanner := bufio.NewScanner(file)
		// optionally, resize scanner's capacity for lines over 64K, see next example
		j = 1
		for scanner.Scan() {
			str = scanner.Text()
			//fmt.Println(str)
			if j == idx {
				if str != "4" {
					logger.Info("str ", str)
					file.Close()
					return true
				}
			}
			j++
		}

		if err := scanner.Err(); err != nil {
			fmt.Println("scanner.Err()")
		}

		file.Close()
		return false
	}
}

func getallpeers() []string {

	var peers = []string{}
	var str string
    var idx int

	file, err := os.Open("../clients/client_ids")
	if err != nil {
		fmt.Println("../clients/client_ids Err()")
	}

	scanner := bufio.NewScanner(file)
	// optionally, resize scanner's capacity for lines over 64K, see next example
	idx = 1
	for scanner.Scan() {
		str = scanner.Text()
		//fmt.Println(str)
		if str != "0" {
			logger.Info("str ", str)
			if tunnel_down(true, idx) {
				peers = append(peers, str)
			}
		}
		idx++
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("scanner.Err()")
	}

	file.Close()

	file, err = os.Open("../servers/server_ids")
	if err != nil {
		fmt.Println("../servers/server_ids Err()")
	}

	scanner = bufio.NewScanner(file)
	// optionally, resize scanner's capacity for lines over 64K, see next example
	idx = 1
	for scanner.Scan() {
		str = scanner.Text()
		//fmt.Println(str)
		if str != "0" {
			logger.Info("str ", str)
			if tunnel_down(true, idx) {
				peers = append(peers, str)
			}
		}
		idx++
	}

	if err := scanner.Err(); err != nil {
		fmt.Println("scanner.Err()")
	}

	file.Close()

	return peers

}

func contains(s []string, e string) bool {
	for _, a := range s {
		if a == e {
			return true
		}
	}
	return false
}

func main() {

	peeridloaded = getallpeers()

	log.SetAllLoggers(log.LevelWarn)
	log.SetLogLevel("rendezvous", "info")
	help := flag.Bool("h", false, "Display Help")
	config, err := ParseFlags()
	if err != nil {
		panic(err)
	}

	if *help {
		fmt.Println("This program demonstrates a simple p2p chat application using libp2p")
		fmt.Println()
		fmt.Println("Usage: Run './chat in two different terminals. Let them connect to the bootstrap nodes, announce themselves and connect to the peers")
		flag.PrintDefaults()
		return
	}

	scalingLimits := rcmgr.InfiniteLimits

	// The resource manager expects a limiter, se we create one from our limits.
	limiter := rcmgr.NewFixedLimiter(scalingLimits)

	// Metrics are enabled by default. If you want to disable metrics, use the
	// WithMetricsDisabled option
	// Initialize the resource manager
	rcm, err := rcmgr.NewResourceManager(limiter, rcmgr.WithMetricsDisabled())
	if err != nil {
		panic(err)
	}

	// Set your own keypair
	fpriv, err := os.ReadFile("priv")
	if err != nil {
		priv, _, err := crypto.GenerateKeyPair(
			crypto.Ed25519, // Select your key type. Ed25519 are nice short
			-1,             // Select key length when possible (i.e. RSA).
		)

		privb, err := crypto.MarshalPrivateKey(priv)
		if err != nil {
			panic(err)
		}
		os.WriteFile("priv", privb, 0666)

		return
	}

	priv, err := crypto.UnmarshalPrivateKey(fpriv)
	if err != nil {
		panic(err)
	}

	// Read from localip file
	flocalip, err := os.ReadFile("../self/localip")
	if err != nil {
		fmt.Println("No localip to use!")
		panic(err)
	}

	mylocalip := string(flocalip)

	// Read from rndsrcport file
	fport, err := os.ReadFile("rndsrcport")
	if err != nil {
		fmt.Println("No random source port to use!")
		panic(err)
	}

	myPort := string(fport)

	fmt.Println("the port from wich we connect ", myPort)

	localwhat := "/ip4/" + mylocalip + "/udp/" + myPort + "/quic-v1"

	opts := []libp2p.Option{libp2p.Identity(priv),
		libp2p.ResourceManager(rcm),
		libp2p.ListenAddrStrings(localwhat)}

	// libp2p.New constructs a new libp2p Host. Other options can be added
	// here.
	host, err := libp2p.New(opts...)
	if err != nil {
		panic(err)
	}
	logger.Info("Host created. We are:", host.ID())
	logger.Info(host.Addrs())

	_, err = os.ReadFile("hostid")
	if err != nil {
		os.WriteFile("hostid", []byte(host.ID().String()), 0666)
        return
	}

	// Set a function as stream handler. This function is called when a peer
	// initiates a connection and starts a stream with this peer.
	host.SetStreamHandler(protocol.ID(config.ProtocolID), handleStream)

	// Start a DHT, for use in peer discovery. We can't just make a new DHT
	// client because we want each peer to maintain its own local copy of the
	// DHT, so that the bootstrapping node of the DHT can go down without
	// inhibiting future peer discovery.
	ctx := context.Background()
	bootstrapPeers := make([]peer.AddrInfo, len(config.BootstrapPeers))
	for i, addr := range config.BootstrapPeers {
		peerinfo, _ := peer.AddrInfoFromP2pAddr(addr)
		bootstrapPeers[i] = *peerinfo
	}
	kademliaDHT, err := dht.New(ctx, host, dht.BootstrapPeers(bootstrapPeers...))
	if err != nil {
		panic(err)
	}

	// Bootstrap the DHT. In the default configuration, this spawns a Background
	// thread that will refresh the peer table every five minutes.
	logger.Debug("Bootstrapping the DHT")
	if err = kademliaDHT.Bootstrap(ctx); err != nil {
		panic(err)
	}

	// Wait a bit to let bootstrapping finish (really bootstrap should block until it's ready, but that isn't the case yet.)
	time.Sleep(1 * time.Second)

	// We use a rendezvous point "meet me here" to announce our location.
	// This is like telling your friends to meet you at the Eiffel Tower.
	logger.Info("Announcing ourselves...")
	routingDiscovery := drouting.NewRoutingDiscovery(kademliaDHT)
	dutil.Advertise(ctx, routingDiscovery, host.ID().String())
	logger.Info("Successfully announced!")

	// Now, look for others who have announced
	// This is like your friend telling you the location to meet you.
	logger.Info("Searching for other peers...")

	//the indexing here is just a hacky way to save the peerid in question as an array element.
	for i := 0; i < len(peeridloaded); i++ {
		go search_and_connect(ctx, host, peeridloaded[i], routingDiscovery, config)
		logger.Info("Searching for other peers...")
	}

	select {}
}
