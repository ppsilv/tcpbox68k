#ifndef PDTERMDISPLAY_H
#define PDTERMDISPLAY_H

#include <QPlainTextEdit>
#include <QKeyEvent>

class PdTermDisplay : public QPlainTextEdit
{
    Q_OBJECT
public:
    explicit PdTermDisplay(QWidget *parent = nullptr);
    
signals:
    void keyPressed(QKeyEvent *event);
    void enterPressed(const QString &text);

protected:
    void keyPressEvent(QKeyEvent *event) override;

private:
    void setupDisplay();
};

#endif // PDTERMDISPLAY_H
