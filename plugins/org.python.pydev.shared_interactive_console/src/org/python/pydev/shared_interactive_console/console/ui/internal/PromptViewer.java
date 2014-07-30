package org.python.pydev.shared_interactive_console.console.ui.internal;

import org.eclipse.jface.text.source.SourceViewer;

public class PromptViewer extends SourceViewer {

    public PromptViewer(TextAndPromptComposite textAndPromptComposite, int styles) {
        super(textAndPromptComposite, null, styles);
    }

}
