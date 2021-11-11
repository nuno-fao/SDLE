import java.rmi.Remote;
import java.rmi.RemoteException;

public interface PubRemoteInterface extends Remote {
    int Put() throws RemoteException;
}