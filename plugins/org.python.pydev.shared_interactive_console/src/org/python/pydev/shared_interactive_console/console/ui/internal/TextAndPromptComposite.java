package org.python.pydev.shared_interactive_console.console.ui.internal;

import org.eclipse.swt.custom.StyledText;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.widgets.Composite;
import org.python.pydev.shared_core.callbacks.ICallbackListener;
import org.python.pydev.shared_interactive_console.console.ui.ScriptConsolePartitioner;
import org.python.pydev.shared_ui.utils.RunInUiThread;

public class TextAndPromptComposite extends Composite {

    private StyledText inputTextWidget;
    private OutputViewer outputViewer;

    int lastX = -1, lastY = -1, lastW = -1, lastH = -1;

    public TextAndPromptComposite(Composite parent, int style) {
        super(parent, style);

    }

    @Override
    public void setBounds(Rectangle rect) {
        setBounds(rect.x, rect.y, rect.width, rect.height);
    }

    @Override
    public void setBounds(int x, int y, int width, int height) {
        lastX = x;
        lastY = y;
        lastW = width;
        lastH = height;
        if (width <= 0 || height <= 0) {
            return;
        }
        super.setBounds(x, y, width, height);

        int requiredOutputSize = 50;

        if (outputViewer != null) {
            StyledText textWidget = outputViewer.getTextWidget();
            int lineCount = textWidget.getLineCount();
            int lineHeight = textWidget.getLineHeight();

            requiredOutputSize = lineCount * lineHeight;
            if (requiredOutputSize > height - 50) {
                requiredOutputSize = height - 50;
            }

            if (textWidget != null) {
                textWidget.setBounds(x, y, width, requiredOutputSize);
            }
        }

        if (inputTextWidget != null) {
            // TODO: Calculate this based on the text that exists on 'text' (50 should be min width, but
            // the prompt should expand if there's no text in 'text').
            inputTextWidget.setBounds(x, y + requiredOutputSize, width, height - requiredOutputSize);
        }
    }

    private void updateBounds() {
        boolean runNowIfInUiThread = true;
        RunInUiThread.async(new Runnable() {

            @Override
            public void run() {
                if (!isDisposed()) {
                    if (lastW != -1 && lastH != -1) {
                        setBounds(lastX, lastY, lastW, lastH);
                    }
                }
            }
        }, runNowIfInUiThread);
    }

    @Override
    public void dispose() {
        super.dispose();
        outputViewer = null;
        this.inputTextWidget = null;
    }

    public void setInputTextWidget(StyledText textWidget) {
        this.inputTextWidget = textWidget;
    }

    public void createOutputViewer(int styles) {
        this.outputViewer = new OutputViewer(this, styles, new ScriptConsolePartitioner());
        this.outputViewer.onTextAppended.registerListener(new ICallbackListener<String>() {

            @Override
            public Object call(String obj) {
                updateBounds();
                return null;
            }
        });
    }

    public OutputViewer getOutputViewer() {
        return this.outputViewer;
    }

    public void clear() {
        if (outputViewer != null) {
            this.outputViewer.getDocument().set("");
            updateBounds();
        }

    }

}