import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: "#111216"

    property int stage

    onStageChanged: {
        if (stage >= 1 && content.opacity === 0) {
            introAnim.start();
        }
        if (stage >= 5) {
            outroAnim.start();
        }
    }

    NumberAnimation {
        id: introAnim
        target: content
        property: "opacity"
        from: 0
        to: 1
        duration: 450
        easing.type: Easing.OutCubic
    }

    NumberAnimation {
        id: outroAnim
        target: content
        property: "opacity"
        to: 0
        duration: 300
        easing.type: Easing.InCubic
    }

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        Canvas {
            id: emblem
            width: Kirigami.Units.gridUnit * 7
            height: Kirigami.Units.gridUnit * 7
            anchors.centerIn: parent
            anchors.verticalCenterOffset: -Kirigami.Units.gridUnit * 1.5
            antialiasing: true

            onPaint: {
                var ctx = getContext("2d");
                var w = width;
                var h = height;
                ctx.reset();

                var grad = ctx.createLinearGradient(w * 0.15, h * 0.15, w * 0.85, h * 0.85);
                grad.addColorStop(0.0, "#3c78ff");
                grad.addColorStop(0.55, "#10a6d4");
                grad.addColorStop(1.0, "#269e9c");

                ctx.beginPath();
                ctx.moveTo(w * 0.5, h * 0.12);
                ctx.lineTo(w * 0.84, h * 0.82);
                ctx.lineTo(w * 0.70, h * 0.82);
                ctx.lineTo(w * 0.50, h * 0.39);
                ctx.lineTo(w * 0.30, h * 0.82);
                ctx.lineTo(w * 0.16, h * 0.82);
                ctx.closePath();
                ctx.fillStyle = grad;
                ctx.fill();

                ctx.beginPath();
                ctx.moveTo(w * 0.31, h * 0.63);
                ctx.quadraticCurveTo(w * 0.50, h * 0.54, w * 0.69, h * 0.63);
                ctx.lineWidth = Math.max(2.5, w * 0.045);
                ctx.lineCap = "round";
                ctx.strokeStyle = "#6296ff";
                ctx.stroke();
            }
        }

        Text {
            id: titleText
            anchors.top: emblem.bottom
            anchors.topMargin: Kirigami.Units.gridUnit * 0.8
            anchors.horizontalCenter: parent.horizontalCenter
            text: "AETHER"
            color: "#e6e9ef"
            font.pixelSize: Math.round(Kirigami.Units.gridUnit * 1.1)
            font.letterSpacing: 6
            font.weight: Font.Medium
        }

        Rectangle {
            id: track
            width: Kirigami.Units.gridUnit * 11
            height: 4
            radius: 2
            color: "#1f2228"
            anchors.top: titleText.bottom
            anchors.topMargin: Kirigami.Units.gridUnit * 1.8
            anchors.horizontalCenter: parent.horizontalCenter

            Rectangle {
                height: parent.height
                radius: parent.radius
                width: Math.max(0, Math.min(1, root.stage / 6)) * parent.width
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "#3c78ff" }
                    GradientStop { position: 1.0; color: "#10a6d4" }
                }

                Behavior on width {
                    NumberAnimation {
                        duration: 280
                        easing.type: Easing.OutCubic
                    }
                }
            }
        }
    }
}
