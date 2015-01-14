moon
====

自用的一些类库

SqlAlchemy Wrap
--------------

对`SQLAlchemy`的封装，模仿`Flask-SQLAlchemy`但是解除了对`Flask`的依赖，可以方便的用在一些非`Flask`代码中。

LazyProxy
--------

把`werkzeug.local`中的`LocalProxy`抄出来，可以用于实现各种全局对象。


Config Tool
-----------

简单的配置文件处理。

    main.py:

    from moon.config import setconf
    setconf("prjname", "~/.user-config", AA="BB")

    
    end of config.py:

    from moon.config import exportconf
    exportconf("prjname", globals())
