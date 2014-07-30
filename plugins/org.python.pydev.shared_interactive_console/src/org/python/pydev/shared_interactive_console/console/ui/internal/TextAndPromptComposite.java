package org.python.pydev.shared_interactive_console.console.ui.internal;

import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Composite;

public class TextAndPromptComposite extends Composite {

    private StyledText text;
    private PromptViewer promptViewer;

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
        if (text != null) {
            // TODO: Calculate this based on the text that exists on 'text' (50 should be min width, but
            // the prompt should expand if there's no text in 'text').
            text.setBounds(x, y, width, height - 50);
        }
        if (promptViewer != null) {
            StyledText textWidget = promptViewer.getTextWidget();
            if (textWidget != null) {
                textWidget.setBounds(x, y + height - 50, width, 50);
            }
        }
    }

    public void setTextWidget(StyledText textWidget) {
        this.text = textWidget;
    }

    public void createPrompt(int styles) {
        PromptViewer textViewer = new PromptViewer(this, styles);
        this.promptViewer = textViewer;
    }

}