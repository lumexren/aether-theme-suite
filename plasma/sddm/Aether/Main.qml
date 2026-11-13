import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: config.color || "#111216"

    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
    property string errorText: ""

    Image {
        anchors.fill: parent
        source: config.background || "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        smooth: true
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#550c0d11" }
            GradientStop { position: 0.6; color: "#33111216" }
            GradientStop { position: 1.0; color: "#880c0d11" }
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        onTriggered: {
            var now = new Date();
            clockTime.text = Qt.formatTime(now, "HH:mm");
            clockDate.text = Qt.formatDate(now, "dddd, d MMMM");
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.errorText = "Authentication failed. Please try again.";
            passwordInput.text = "";
            passwordInput.forceActiveFocus();
        }
        function onLoginSucceeded() {
            root.errorText = "";
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: loginCard.top
        anchors.bottomMargin: 36
        spacing: 6
        visible: config.showClock !== "false"

        Text {
            id: clockTime
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(new Date(), "HH:mm")
            color: "#f4f4f4"
            font.family: config.font || "Google Sans"
            font.pixelSize: 64
            font.weight: Font.Medium
        }

        Text {
            id: clockDate
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), "dddd, d MMMM")
            color: "#9199a8"
            font.family: config.font || "Google Sans"
            font.pixelSize: 16
        }
    }

    Rectangle {
        id: loginCard
        width: 390
        height: cardLayout.implicitHeight + 56
        radius: 14
        color: "#e616181d"
        border.color: "#262a33"
        border.width: 1
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 40

        ColumnLayout {
            id: cardLayout
            anchors.fill: parent
            anchors.margins: 28
            spacing: 14

            QQC2.ComboBox {
                id: userSelector
                Layout.fillWidth: true
                model: userModel
                textRole: "realName"
                currentIndex: root.userIndex
                onCurrentIndexChanged: root.userIndex = currentIndex

                background: Rectangle {
                    radius: 8
                    color: "#111216"
                    border.color: userSelector.activeFocus ? "#3c78ff" : "#1f2228"
                    border.width: 1
                }

                contentItem: Text {
                    leftPadding: 12
                    text: userSelector.displayText || (userModel.lastUser || "User")
                    color: "#e6e9ef"
                    font.family: config.font || "Google Sans"
                    font.pixelSize: 14
                    verticalAlignment: Text.AlignVCenter
                }
            }

            QQC2.TextField {
                id: passwordInput
                Layout.fillWidth: true
                Layout.preferredHeight: 42
                echoMode: TextInput.Password
                placeholderText: "Password"
                placeholderTextColor: "#707888"
                color: "#f4f4f4"
                font.family: config.font || "Google Sans"
                font.pixelSize: 14
                focus: true

                background: Rectangle {
                    radius: 8
                    color: "#111216"
                    border.color: passwordInput.activeFocus ? "#3c78ff" : "#1f2228"
                    border.width: passwordInput.activeFocus ? 1.5 : 1
                }

                Keys.onReturnPressed: signInBtn.clicked()
                Keys.onEnterPressed: signInBtn.clicked()
            }

            Text {
                visible: root.errorText.length > 0
                text: root.errorText
                color: "#f13460"
                font.family: config.font || "Google Sans"
                font.pixelSize: 12
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                QQC2.ComboBox {
                    id: sessionSelector
                    Layout.fillWidth: true
                    Layout.preferredHeight: 40
                    model: sessionModel
                    textRole: "name"
                    currentIndex: root.sessionIndex
                    onCurrentIndexChanged: root.sessionIndex = currentIndex

                    background: Rectangle {
                        radius: 8
                        color: "#1a1d24"
                        border.color: "#262a33"
                        border.width: 1
                    }

                    contentItem: Text {
                        leftPadding: 10
                        text: sessionSelector.displayText
                        color: "#abb2bf"
                        font.family: config.font || "Google Sans"
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                }

                QQC2.Button {
                    id: signInBtn
                    text: "Sign In"
                    Layout.preferredWidth: 112
                    Layout.preferredHeight: 40

                    background: Rectangle {
                        radius: 8
                        color: signInBtn.pressed ? "#3062d6" : (signInBtn.hovered ? "#5186ff" : "#3c78ff")
                    }

                    contentItem: Text {
                        text: signInBtn.text
                        color: "#ffffff"
                        font.family: config.font || "Google Sans"
                        font.pixelSize: 14
                        font.weight: Font.Medium
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        var user = userSelector.currentText || userModel.lastUser;
                        sddm.login(user, passwordInput.text, root.sessionIndex);
                    }
                }
            }
        }
    }

    Row {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 28
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 24

        Repeater {
            model: [
                { label: "Suspend", enabled: sddm.canSuspend, action: function() { sddm.suspend(); } },
                { label: "Restart", enabled: sddm.canReboot, action: function() { sddm.reboot(); } },
                { label: "Shut Down", enabled: sddm.canPowerOff, action: function() { sddm.powerOff(); } }
            ]

            QQC2.Button {
                visible: modelData.enabled
                text: modelData.label
                onClicked: modelData.action()
                background: Rectangle {
                    radius: 6
                    color: parent.hovered ? "#262a33" : "#111216"
                    border.color: "#1f2228"
                    border.width: 1
                }
                contentItem: Text {
                    leftPadding: 10
                    rightPadding: 10
                    text: parent.text
                    color: "#9199a8"
                    font.family: config.font || "Google Sans"
                    font.pixelSize: 12
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }
}
