#ifndef PDTERMTERMINAL_H
#define PDTERMTERMINAL_H

#include <QMainWindow>
#include <QPlainTextEdit>
#include "PdTermSerial.h"
#include "PdTermDisplay.h"

class TerminalDisplay;

class PdTermTerminal : public QMainWindow
{
    Q_OBJECT
public:
    explicit PdTermTerminal(QWidget *parent = nullptr);
    ~PdTermTerminal();

    void showStatusMessage(const QString &message);

private slots:
    void handleDataReceived(const QByteArray &data);
    void handleSerialError(const QString &error);

private:
    void setupUI();
    void setupConnections();

    PdTermDisplay *terminalDisplay;
    PdTermSerial *serialHandler;
    QComboBox *portCombo;
    QString inputBuffer;
};

#endif // PDTERMTERMINAL_H
