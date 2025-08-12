#include "PdTermDisplay.h"
#include <QPalette>
#include <QFont>
#include <QDebug>

PdTermDisplay::PdTermDisplay(QWidget *parent) : QPlainTextEdit(parent)
{
    setupDisplay();
}

void PdTermDisplay::setupDisplay()
{
    // Configurações básicas do display
    setReadOnly(false);
    setUndoRedoEnabled(false);
    setMaximumBlockCount(1000);
    setCursorWidth(2);
    setFocusPolicy(Qt::StrongFocus);
    
    // Configuração do estilo (fundo preto e texto verde)
    QPalette palette = this->palette();
    palette.setColor(QPalette::Base, Qt::black);       // Fundo preto
    palette.setColor(QPalette::Text, Qt::green);       // Texto verde
    palette.setColor(QPalette::Highlight, Qt::darkGreen); // Seleção verde escuro
    palette.setColor(QPalette::HighlightedText, Qt::black); // Texto selecionado preto
    setPalette(palette);
    
    // Fonte monoespaçada
    QFont font("Monospace", 10);
    font.setStyleHint(QFont::TypeWriter);
    setFont(font);
}

void PdTermDisplay::keyPressEvent(QKeyEvent *event)
{
    emit keyPressed(event);
    
    if (event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) {
        QString text = textCursor().block().text();
        emit enterPressed(text);
        appendPlainText("");  // Nova linha
    } else {
        QPlainTextEdit::keyPressEvent(event);
    }
}
