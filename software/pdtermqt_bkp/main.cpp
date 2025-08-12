#include "SerialTerminal.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    SerialTerminal terminal;
    terminal.show();
    return app.exec();
}
