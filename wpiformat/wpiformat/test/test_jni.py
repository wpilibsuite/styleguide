import os

from .test_tasktest import *
from wpiformat.jni import Jni


def test_jni():
    test = TaskTest(Jni())

    # Input args go to next line even if they fit on same line
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_TestJNI_testFunc(JNIEnv* env, jclass) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     TestJNI"
        + os.linesep
        + " * Method:    testFunc"
        + os.linesep
        + " * Signature: ()V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_TestJNI_testFunc"
        + os.linesep
        + "  (JNIEnv* env, jclass)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Input aligned to "(" and args past end of line
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent(JNIEnv* env,"
        + os.linesep
        + "                                                                 jclass,"
        + os.linesep
        + "                                                                 jint source) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    setCameraExposureHoldCurrent"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent"
        + os.linesep
        + "  (JNIEnv* env, jclass, jint source)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Args in input on line after "(" and args length > 80 characters
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame("
        + os.linesep
        + "    JNIEnv *env, jclass, jint source, jlong imageNativeObj) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    putSourceFrame"
        + os.linesep
        + " * Signature: (IJ)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame"
        + os.linesep
        + "  (JNIEnv *env, jclass, jint source, jlong imageNativeObj)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Args > 80 characters long
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT jint JNICALL Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty("
        + os.linesep
        + "    JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum,"
        + os.linesep
        + "    jint maximum, jint step, jint defaultValue, jint value) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    createSourceProperty"
        + os.linesep
        + " * Signature: (ILjava/lang/String;IIIIII)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty"
        + os.linesep
        + "  (JNIEnv *env, jclass, jint source, jstring name, jint kind, jint minimum,"
        + os.linesep
        + "   jint maximum, jint step, jint defaultValue, jint value)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Ensure fixes clang-format output aligned with "("
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance(JNIEnv*,"
        + os.linesep
        + "                                                                 jclass) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jclass)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Idempotence for same code
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jclass)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Idempotence for same code with named jclass variable
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jclass class)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Check signature that breaks verbose regexes
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntry"
        + os.linesep
        + " * Signature: (ILjava/lang/String;)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry(JNIEnv* env, jclass,"
        + os.linesep
        + "                                                           jint inst,"
        + os.linesep
        + "                                                           jstring key) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntry"
        + os.linesep
        + " * Signature: (ILjava/lang/String;)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry"
        + os.linesep
        + "  (JNIEnv* env, jclass, jint inst, jstring key)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Function with array type as argument
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntries"
        + os.linesep
        + " * Signature: (ILjava/lang/String;I)[I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jintArray JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries(JNIEnv* env,"
        + os.linesep
        + "                                                             jclass, jint inst,"
        + os.linesep
        + "                                                             jstring prefix,"
        + os.linesep
        + "                                                             jint types) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntries"
        + os.linesep
        + " * Signature: (ILjava/lang/String;I)[I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jintArray JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries"
        + os.linesep
        + "  (JNIEnv* env, jclass, jint inst, jstring prefix, jint types)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Ensure functions with overloads are handled correctly
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    setRaw"
        + os.linesep
        + " * Signature: (IJ[BZ)Z"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jboolean JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_setRaw__IJ_3BZ"
        + os.linesep
        + "  (JNIEnv* env, jclass, jint entry, jlong time, jbyteArray value,"
        + os.linesep
        + "   jboolean force)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure text before JNIEXPORT and after args and ")" is handled correctly
    # as well as two JNI functions in a row
    test.add_input(
        "./TestJNI.cpp",
        "/**"
        + os.linesep
        + " *"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jclass)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::GetDefaultInstance();"
        + os.linesep
        + "}"
        + os.linesep
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jclass)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getDefaultInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jclass)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::GetDefaultInstance();"
        + os.linesep
        + "}"
        + os.linesep
        + os.linesep
        + "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jclass)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Handle function declarations properly
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getDefaultInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jclass);"
        + os.linesep
        + os.linesep
        + "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jclass)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Handle functions whose arguments don't have variable names properly
    test.add_input(
        "./DigitalGlitchFilterJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI"
        + os.linesep
        + " * Method:    cleanFilter"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter"
        + os.linesep
        + "  (JNIEnv *, jclass, jint)"
        + os.linesep
        + "{"
        + os.linesep
        + "  HAL_CleanFilter(handle);"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI"
        + os.linesep
        + " * Method:    cleanFilter"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter"
        + os.linesep
        + "  (JNIEnv *, jclass, jint)"
        + os.linesep
        + "{"
        + os.linesep
        + "  HAL_CleanFilter(handle);"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Input args go to next line even if they fit on same line
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_TestJNI_testFunc(JNIEnv* env, jobject) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     TestJNI"
        + os.linesep
        + " * Method:    testFunc"
        + os.linesep
        + " * Signature: ()V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_TestJNI_testFunc"
        + os.linesep
        + "  (JNIEnv* env, jobject)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Input aligned to "(" and args past end of line
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent(JNIEnv* env,"
        + os.linesep
        + "                                                                 jobject,"
        + os.linesep
        + "                                                                 jint source) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    setCameraExposureHoldCurrent"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_setCameraExposureHoldCurrent"
        + os.linesep
        + "  (JNIEnv* env, jobject, jint source)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Args in input on line after "(" and args length > 80 characters
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT void JNICALL Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame("
        + os.linesep
        + "    JNIEnv *env, jobject, jint source, jlong imageNativeObj) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    putSourceFrame"
        + os.linesep
        + " * Signature: (IJ)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_putSourceFrame"
        + os.linesep
        + "  (JNIEnv *env, jobject, jint source, jlong imageNativeObj)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Args > 80 characters long
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT jint JNICALL Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty("
        + os.linesep
        + "    JNIEnv *env, jobject, jint source, jstring name, jint kind, jint minimum,"
        + os.linesep
        + "    jint maximum, jint step, jint defaultValue, jint value) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_cscore_CameraServerJNI"
        + os.linesep
        + " * Method:    createSourceProperty"
        + os.linesep
        + " * Signature: (ILjava/lang/String;IIIIII)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_cscore_CameraServerJNI_createSourceProperty"
        + os.linesep
        + "  (JNIEnv *env, jobject, jint source, jstring name, jint kind, jint minimum,"
        + os.linesep
        + "   jint maximum, jint step, jint defaultValue, jint value)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Ensure fixes clang-format output aligned with "("
    test.add_input(
        "./TestJNI.cpp",
        "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance(JNIEnv*,"
        + os.linesep
        + "                                                                 jobject) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jobject)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Idempotence for same code
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jobject)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Idempotence for same code with named jobject variable
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv*, jobject class)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Check signature that breaks verbose regexes
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntry"
        + os.linesep
        + " * Signature: (ILjava/lang/String;)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry(JNIEnv* env, jobject,"
        + os.linesep
        + "                                                           jint inst,"
        + os.linesep
        + "                                                           jstring key) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntry"
        + os.linesep
        + " * Signature: (ILjava/lang/String;)I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntry"
        + os.linesep
        + "  (JNIEnv* env, jobject, jint inst, jstring key)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Function with array type as argument
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntries"
        + os.linesep
        + " * Signature: (ILjava/lang/String;I)[I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jintArray JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries(JNIEnv* env,"
        + os.linesep
        + "                                                             jobject, jint inst,"
        + os.linesep
        + "                                                             jstring prefix,"
        + os.linesep
        + "                                                             jint types) {"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getEntries"
        + os.linesep
        + " * Signature: (ILjava/lang/String;I)[I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jintArray JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getEntries"
        + os.linesep
        + "  (JNIEnv* env, jobject, jint inst, jstring prefix, jint types)"
        + os.linesep
        + "{"
        + os.linesep,
        True,
    )

    # Ensure functions with overloads are handled correctly
    test.add_input(
        "./NetworkTablesJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    setRaw"
        + os.linesep
        + " * Signature: (IJ[BZ)Z"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jboolean JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_setRaw__IJ_3BZ"
        + os.linesep
        + "  (JNIEnv* env, jobject, jint entry, jlong time, jbyteArray value,"
        + os.linesep
        + "   jboolean force)"
        + os.linesep
        + "{"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Ensure text before JNIEXPORT and after args and ")" is handled correctly
    # as well as two JNI functions in a row
    test.add_input(
        "./TestJNI.cpp",
        "/**"
        + os.linesep
        + " *"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jobject)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::GetDefaultInstance();"
        + os.linesep
        + "}"
        + os.linesep
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jobject)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getDefaultInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jobject)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::GetDefaultInstance();"
        + os.linesep
        + "}"
        + os.linesep
        + os.linesep
        + "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jobject)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    # Handle function declarations properly
    test.add_input(
        "./TestJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    getDefaultInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_getDefaultInstance"
        + os.linesep
        + "  (JNIEnv *, jobject);"
        + os.linesep
        + os.linesep
        + "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_networktables_NetworkTablesJNI"
        + os.linesep
        + " * Method:    createInstance"
        + os.linesep
        + " * Signature: ()I"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT jint JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_networktables_NetworkTablesJNI_createInstance"
        + os.linesep
        + "  (JNIEnv *, jobject)"
        + os.linesep
        + "{"
        + os.linesep
        + "  return nt::CreateInstance();"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_latest_input_as_output(True)

    # Handle functions whose arguments don't have variable names properly
    test.add_input(
        "./DigitalGlitchFilterJNI.cpp",
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI"
        + os.linesep
        + " * Method:    cleanFilter"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter"
        + os.linesep
        + "  (JNIEnv *, jobject, jint)"
        + os.linesep
        + "{"
        + os.linesep
        + "  HAL_CleanFilter(handle);"
        + os.linesep
        + "}"
        + os.linesep,
    )
    test.add_output(
        "/*"
        + os.linesep
        + " * Class:     edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI"
        + os.linesep
        + " * Method:    cleanFilter"
        + os.linesep
        + " * Signature: (I)V"
        + os.linesep
        + " */"
        + os.linesep
        + "JNIEXPORT void JNICALL"
        + os.linesep
        + "Java_edu_wpi_first_wpilibj_hal_DigitalGlitchFilterJNI_cleanFilter"
        + os.linesep
        + "  (JNIEnv *, jobject, jint)"
        + os.linesep
        + "{"
        + os.linesep
        + "  HAL_CleanFilter(handle);"
        + os.linesep
        + "}"
        + os.linesep,
        True,
    )

    test.run(OutputType.FILE)
