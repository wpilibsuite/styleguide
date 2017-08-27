import os

from test.tasktest import *
from wpiformat.jni import Jni


def test_jni():
    test = TaskTest(Jni())

    # Input args go to next line even if they fit on same line
    test.add_input("./TestJNI.cpp",
        "JNIEXPORT void JNICALL" + os.linesep + \
        "Java_TestJNI_testFunc(JNIEnv* env, jclass) {" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     TestJNI" + os.linesep + \
        " * Method:    testFunc" + os.linesep + \
        " * Signature: ()V" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT void JNICALL" + os.linesep + \
        "Java_TestJNI_testFunc" + os.linesep + \
        "  (JNIEnv* env, jclass)" + os.linesep + \
        "{" + os.linesep, True, True)

    # Input aligned to "(" and args past end of line
    test.add_input("./TestJNI.cpp",
        "JNIEXPORT void JNICALL" + os.linesep + \
        "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent(JNIEnv* env," + os.linesep + \
        "                                                                 jclass," + os.linesep + \
        "                                                                 jint source) {" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     edu_wpi_cscore_CameraServerJNI" + os.linesep + \
        " * Method:    setCameraExposureHoldCurrent" + os.linesep + \
        " * Signature: (I)V" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT void JNICALL" + os.linesep + \
        "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent" + os.linesep + \
        "  (JNIEnv* env, jclass, jint source)" + os.linesep + \
"{" + os.linesep, True, True)

    # Args in input on line after "(" and args length > 80 characters
    test.add_input("./TestJNI.cpp",
        "JNIEXPORT void JNICALL Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame(" + os.linesep + \
"    JNIEnv *env, jclass, jint source, jlong imageNativeObj) {" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     edu_wpi_cscore_CameraServerJNI" + os.linesep + \
        " * Method:    putSourceFrame" + os.linesep + \
        " * Signature: (IJ)V" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT void JNICALL" + os.linesep + \
        "Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame" + os.linesep + \
"  (JNIEnv *env, jclass, jint source, jlong imageNativeObj)" + os.linesep + \
"{" + os.linesep, True, True)

    # Args > 80 characters long
    test.add_input("./TestJNI.cpp",
        "JNIEXPORT jint JNICALL Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty(" + os.linesep + \
"    JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum," + os.linesep + \
"    jint maximum, jint step, jint defaultValue, jint value) {" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     edu_wpi_cscore_CameraServerJNI" + os.linesep + \
        " * Method:    createSourceProperty" + os.linesep + \
        " * Signature: (ILjava/lang/String;IIIIII)I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty" + os.linesep + \
"  (JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum," + os.linesep + \
"   jint maximum, jint step, jint defaultValue, jint value)" + os.linesep + \
"{" + os.linesep, True, True)

    # Ensure fixes clang-format output aligned with "("
    test.add_input("./TestJNI.cpp",
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance(JNIEnv*," + os.linesep + \
"                                                                 jclass) {" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     edu_wpi_first_networktables_NetworkTablesJNI" + os.linesep + \
        " * Method:    createInstance" + os.linesep + \
        " * Signature: ()I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance" + os.linesep + \
        "  (JNIEnv*, jclass)" + os.linesep + \
        "{" + os.linesep, True, True)

    # Idempotence for same code
    test.add_input("./TestJNI.cpp",
        "/*" + os.linesep + \
        " * Class:     edu_wpi_first_networktables_NetworkTablesJNI" + os.linesep + \
        " * Method:    createInstance" + os.linesep + \
        " * Signature: ()I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance" + os.linesep + \
        "  (JNIEnv*, jclass)" + os.linesep + \
        "{" + os.linesep)
    test.add_latest_input_as_output(True)

    # Idempotence for same code with named jclass variable
    test.add_input("./TestJNI.cpp",
        "/*" + os.linesep + \
        " * Class:     edu_wpi_first_networktables_NetworkTablesJNI" + os.linesep + \
        " * Method:    createInstance" + os.linesep + \
        " * Signature: ()I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance" + os.linesep + \
        "  (JNIEnv*, jclass class)" + os.linesep + \
        "{" + os.linesep)
    test.add_latest_input_as_output(True)

    # Ensure text before JNIEXPORT and after args and ")" is handled correctly
    # as well as two JNI functions in a row
    test.add_input("./TestJNI.cpp",
        "/**" + os.linesep + \
        " *" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance" + os.linesep + \
        "  (JNIEnv *, jclass)" + os.linesep + \
        "{" + os.linesep + \
        "  return nt::GetDefaultInstance();" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance" + os.linesep + \
        "  (JNIEnv *, jclass)" + os.linesep + \
        "{" + os.linesep + \
        "  return nt::CreateInstance();" + os.linesep + \
        "}" + os.linesep)
    test.add_output(
        "/*" + os.linesep + \
        " * Class:     edu_wpi_first_networktables_NetworkTablesJNI" + os.linesep + \
        " * Method:    getDefaultInstance" + os.linesep + \
        " * Signature: ()I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance" + os.linesep + \
        "  (JNIEnv *, jclass)" + os.linesep + \
        "{" + os.linesep + \
        "  return nt::GetDefaultInstance();" + os.linesep + \
        "}" + os.linesep + \
        os.linesep + \
        "/*" + os.linesep + \
        " * Class:     edu_wpi_first_networktables_NetworkTablesJNI" + os.linesep + \
        " * Method:    createInstance" + os.linesep + \
        " * Signature: ()I" + os.linesep + \
        " */" + os.linesep + \
        "JNIEXPORT jint JNICALL" + os.linesep + \
        "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance" + os.linesep + \
        "  (JNIEnv *, jclass)" + os.linesep + \
        "{" + os.linesep + \
        "  return nt::CreateInstance();" + os.linesep + \
        "}" + os.linesep, True, True)

    test.run(OutputType.FILE)
