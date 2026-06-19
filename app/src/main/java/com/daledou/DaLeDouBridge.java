package com.daledou;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

/**
 * Python Bridge 辅助类
 * 封装通用 Python 调用
 */
public class DaLeDouBridge {

    private static PyObject getBridge() {
        return Python.getInstance().getModule("bridge");
    }

    public static String runModule(String module) {
        return getBridge().callAttr("run_module", module).toString();
    }

    public static void stopTask() {
        getBridge().callAttr("stop_task");
    }

    public static String readLog() {
        return getBridge().callAttr("read_log").toString();
    }

    public static String getQQList() {
        return getBridge().callAttr("get_qq_list").toString();
    }

    public static String getTaskList(String module) {
        return getBridge().callAttr("get_task_list", module).toString();
    }

    public static void saveTaskRegister(String module, String data) {
        getBridge().callAttr("save_task_register", module, data);
    }
}
