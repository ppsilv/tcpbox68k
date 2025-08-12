#include "PdTermTerminal.h"
#include "PdTermDisplay.h"
#include <QMenuBar>
#include <QMenu>
#include <QAction>
#include <QStatusBar>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QDebug>

PdTermTerminal::PdTermTerminal(QWidget *parent) : QMainWindow(parent)
{
    serialHandler = new PdTermSerial(this);
    setupUI();
    setupConnections();
}

PdTermTerminal::~PdTermTerminal()
{
    delete serialHandler;
}

void PdTermTerminal::setupUI()
{
    // Configuração da janela principal
    setWindowTitle("Terminal Serial");
    resize(800, 600);

    // Barra de menus
    QMenuBar *menuBar = new QMenuBar();
    QMenu *serialMenu = menuBar->addMenu("Serial");
    QMenu *transferMenu = menuBar->addMenu("Transferência");

    // Ações do menu
    QAction *connectAction = new QAction("Conectar", this);
    QAction *disconnectAction = new QAction("Desconectar", this);
    QAction *refreshAction = new QAction("Atualizar Portas", this);
    QAction *exitAction = new QAction("Sair", this);
    QAction *sendXmodemAction = new QAction("Enviar Arquivo (XMODEM)", this);

    serialMenu->addActions({connectAction, disconnectAction, refreshAction});
    serialMenu->addSeparator();
    serialMenu->addAction(exitAction);
    transferMenu->addAction(sendXmodemAction);

    setMenuBar(menuBar);

    // Widget central
    QWidget *centralWidget = new QWidget(this);
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

    // Terminal display
    terminalDisplay = new PdTermDisplay(this);
    terminalDisplay->setReadOnly(false);
    terminalDisplay->setUndoRedoEnabled(false);
    terminalDisplay->setMaximumBlockCount(1000);

    // Barra de controle
    QHBoxLayout *controlLayout = new QHBoxLayout();
    portCombo = new QComboBox();
    QLabel *portLabel = new QLabel("Porta:");
    controlLayout->addWidget(portLabel);
    controlLayout->addWidget(portCombo);

    // Layout principal
    mainLayout->addLayout(controlLayout);
    mainLayout->addWidget(terminalDisplay);
    setCentralWidget(centralWidget);

    // Barra de status
    statusBar()->showMessage("Desconectado - Nenhuma porta selecionada");
}

void PdTermTerminal::setupConnections()
{
    // Conectar sinais do serial handler
    connect(serialHandler, &PdTermSerial::dataReceived, this, &PdTermTerminal::handleDataReceived);
    connect(serialHandler, &PdTermSerial::errorOccurred, this, &PdTermTerminal::handleSerialError);
    connect(serialHandler, &PdTermSerial::statusChanged, statusBar(), &QStatusBar::showMessage);

    // Conectar ações do menu
    connect(refreshAction, &QAction::triggered, [this]() {
        serialHandler->refreshPorts(portCombo);
    });
    
    connect(connectAction, &QAction::triggered, [this]() {
        serialHandler->connectSerial(portCombo->currentText());
    });
    
    connect(disconnectAction, &QAction::triggered, serialHandler, &PdTermSerial::disconnectSerial);
    connect(exitAction, &QAction::triggered, this, &QWidget::close);
}

void PdTermTerminal::handleDataReceived(const QByteArray &data)
{
    terminalDisplay->insertPlainText(QString::fromUtf8(data));
    QTextCursor cursor = terminalDisplay->textCursor();
    cursor.movePosition(QTextCursor::End);
    terminalDisplay->setTextCursor(cursor);
}

void PdTermTerminal::handleSerialError(const QString &error)
{
    QMessageBox::critical(this, "Erro Serial", error);
    terminalDisplay->appendPlainText("\n[ERRO: " + error + "]");
}

void PdTermTerminal::showStatusMessage(const QString &message)
{
    terminalDisplay->appendPlainText(message);
    statusBar()->showMessage(message, 3000);
}
