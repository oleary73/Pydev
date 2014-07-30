package org.python.pydev.shared_interactive_console.console.ui.internal;

import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Composite;
import org.python.pydev.shared_interactive_console.console.ui.ScriptConsolePartitioner;

public class TextAndPromptComposite extends Composite {

    private StyledText inputTextWidget;
    private OutputViewer outputViewer;

    public TextAndPromptComposite(Composite parent, int style) {
        super(parent, style);

    }

    @Override
    public void setBounds(Rectangle rect) {
        setBounds(rect.x, rect.y, rect.width, rect.height);
    }

    @Override
    public void setBounds(int x, int y, int width, int height) {
        super.setBounds(x, y, width, height);
        if (inputTextWidget != null) {
            // TODO: Calculate this based on the text that exists on 'text' (50 should be min width, but
            // the prompt should expand if there's no text in 'text').
            inputTextWidget.setBounds(x, y + height - 50, width, 50);
        }
        if (outputViewer != null) {
            StyledText textWidget = outputViewer.getTextWidget();
            if (textWidget != null) {
                textWidget.setBounds(x, y, width, height - 50);
            }
        }
    }

    public void setInputTextWidget(StyledText textWidget) {
        this.inputTextWidget = textWidget;
    }

    public void createOutputViewer(int styles) {
        this.outputViewer = new OutputViewer(this, styles, new ScriptConsolePartitioner());
    }

    public OutputViewer getOutputViewer() {
        return this.outputViewer;
    }

}