import java.net.MalformedURLException;
import java.rmi.AlreadyBoundException;
import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.RemoteObject;
import java.rmi.server.UnicastRemoteObject;

import static java.lang.Integer.parseInt;

public class Pub implements PubRemoteInterface {
    private static Pub pub = null;

    @Override
    public int Put() throws RemoteException {
        System.out.println("PUT");
        return 0;
    }

    public Pub(String name, int port) throws RemoteException {
        try{
            PubRemoteInterface manager = (PubRemoteInterface) UnicastRemoteObject.exportObject(this,0);
            Registry rmiRegistry = LocateRegistry.createRegistry(port);
            rmiRegistry.bind(name,manager);
            System.err.println("Pub ready");
        }
        catch(RemoteException | AlreadyBoundException e){
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws RemoteException {
        pub = new Pub(args[0],parseInt(args[1]));
    }
}
