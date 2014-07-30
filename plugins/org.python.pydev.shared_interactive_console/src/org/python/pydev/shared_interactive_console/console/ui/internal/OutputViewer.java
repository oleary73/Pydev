package org.python.pydev.shared_interactive_console.console.ui.internal;

import java.util.List;

import org.eclipse.debug.ui.console.IConsoleLineTracker;
import org.eclipse.jface.text.BadLocationException;
import org.eclipse.jface.text.IDocument;
import org.eclipse.jface.text.IDocumentPartitioner;
import org.eclipse.jface.text.Region;
import org.eclipse.ui.console.IConsoleDocumentPartitioner;
import org.eclipse.ui.console.TextConsole;
import org.eclipse.ui.console.TextConsoleViewer;
import org.python.pydev.shared_core.log.Log;
import org.python.pydev.shared_core.string.TextSelectionUtils;
import org.python.pydev.shared_core.structure.Tuple;
import org.python.pydev.shared_interactive_console.console.ui.IConsoleStyleProvider;
import org.python.pydev.shared_interactive_console.console.ui.ScriptConsole;
import org.python.pydev.shared_interactive_console.console.ui.ScriptConsolePartitioner;
import org.python.pydev.shared_interactive_console.console.ui.ScriptStyleRange;

public class OutputViewer extends TextConsoleViewer {

    /**
     * Console line trackers (for hyperlinking)
     */
    private List<IConsoleLineTracker> consoleLineTrackers;
    private IConsoleStyleProvider iConsoleStyleProvider;
    private TextConsole console;

    public OutputViewer(TextAndPromptComposite textAndPromptComposite, int styles,
            final ScriptConsolePartitioner partitioner) {
        this(textAndPromptComposite, styles, partitioner, new TextConsole("Internal console", null, null, false) {

            @Override
            protected IConsoleDocumentPartitioner getPartitioner() {
                return partitioner;
            }
        });

    }

    public OutputViewer(TextAndPromptComposite textAndPromptComposite, int styles,
            final ScriptConsolePartitioner partitioner, TextConsole console) {
        super(textAndPromptComposite, console);
        this.console = console;

        IDocument document = getDocument();
        document.setDocumentPartitioner(partitioner);
        partitioner.connect(document);

    }

    public void configure(ScriptConsole console) {
        this.iConsoleStyleProvider = console.createStyleProvider();
        this.consoleLineTrackers = console.createLineTrackers(this.console);
    }

    @Override
    protected void handleDispose() {
        this.console = null;
        this.consoleLineTrackers = null;
        this.iConsoleStyleProvider = null;
    }

    /**
     * Adds a given style range to the partitioner.
     *
     * Note that the style must be added before the actual text is added! (because as
     * soon as it's added, the style is asked for).
     *
     * @param style the style to be added.
     */
    private void addToPartitioner(ScriptStyleRange style) {
        IDocumentPartitioner partitioner = getDocument().getDocumentPartitioner();
        if (partitioner instanceof ScriptConsolePartitioner) {
            ScriptConsolePartitioner scriptConsolePartitioner = (ScriptConsolePartitioner) partitioner;
            scriptConsolePartitioner.addRange(style);
        }
    }

    /**
     * Adds some text that came as an output to stdout or stderr to the console.
     *
     * @param out the text that should be added
     * @param stdout true if it came from stdout and also if it came from stderr
     */
    public void addToConsoleView(String out, boolean stdout) {
        if (out.length() == 0) {
            return; //nothing to add!
        }
        IDocument doc = getDocument();
        int start = doc.getLength();

        IConsoleStyleProvider styleProvider = iConsoleStyleProvider;
        Tuple<List<ScriptStyleRange>, String> style = null;
        if (styleProvider != null) {
            if (stdout) {
                style = styleProvider.createInterpreterOutputStyle(out, start);
            } else { //stderr
                style = styleProvider.createInterpreterErrorStyle(out, start);
            }
            if (style != null) {
                for (ScriptStyleRange s : style.o1) {
                    addToPartitioner(s);
                }
            }
        }
        if (style != null) {
            appendText(style.o2);
        }

        TextSelectionUtils ps = new TextSelectionUtils(doc, start);
        int cursorLine = ps.getCursorLine();
        int numberOfLines = doc.getNumberOfLines();

        //right after appending the text, let's notify line trackers
        for (int i = cursorLine; i < numberOfLines; i++) {
            try {
                int offset = ps.getLineOffset(i);
                int endOffset = ps.getEndLineOffset(i);

                Region region = new Region(offset, endOffset - offset);

                for (IConsoleLineTracker lineTracker : this.consoleLineTrackers) {
                    lineTracker.lineAppended(region);
                }
            } catch (Exception e) {
                Log.log(e);
            }
        }
    }

    /**
     * Appends some text at the end of the document.
     *
     * @param text the text to be added.
     */
    protected void appendText(String text) {
        IDocument doc = getDocument();
        int initialOffset = doc.getLength();
        try {
            doc.replace(initialOffset, 0, text);
        } catch (BadLocationException e) {
            Log.log(e);
        }
    }

}
