package org.python.pydev.shared_ui.utils;

import org.eclipse.swt.custom.StyledText;

public class ShowScrollbarOnlyWhenNeeded {

    private StyledText textWidget;

    public ShowScrollbarOnlyWhenNeeded(StyledText textWidget) {
        this.textWidget = textWidget;

        //TODO: Add better support for this (leave hidden but show when we hover over it).
        textWidget.getHorizontalBar().setVisible(false);
        textWidget.getVerticalBar().setVisible(false);
    }

}
