import java.rmi.Remote;
import java.rmi.RemoteException;

public interface SubRemoteInterface extends Remote {
    int Get() throws RemoteException;

    int Subscribe() throws RemoteException;

    int Unsubscribe() throws RemoteException;
}