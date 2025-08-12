#ifndef PDTERMSERIAL_H
#define PDTERMSERIAL_H

#include <QObject>
#include <QSerialPort>
#include <QSerialPortInfo>

class PdTermSerial : public QObject
{
    Q_OBJECT
public:
    explicit PdTermSerial(QObject *parent = nullptr);
    ~PdTermSerial();

    void refreshPorts(QComboBox *portCombo);
    bool connectSerial(const QString &portName);
    void disconnectSerial();
    void sendData(const QByteArray &data);
    bool isConnected() const;

signals:
    void dataReceived(const QByteArray &data);
    void errorOccurred(const QString &error);
    void statusChanged(const QString &status);

private slots:
    void handleReadyRead();
    void handleError(QSerialPort::SerialPortError error);

private:
    QSerialPort *serial;
};

#endif // PDTERMSERIAL_H
