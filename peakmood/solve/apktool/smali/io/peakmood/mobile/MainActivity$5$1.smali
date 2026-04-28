.class Lio/peakmood/mobile/MainActivity$5$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lio/peakmood/mobile/MainActivity$5;->run()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lio/peakmood/mobile/MainActivity$5;


# direct methods
.method constructor <init>(Lio/peakmood/mobile/MainActivity$5;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x8010
        }
        names = {
            null
        }
    .end annotation

    .line 355
    iput-object p1, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .locals 4

    .line 358
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    const/4 v1, 0x0

    invoke-static {v0, v1}, Lio/peakmood/mobile/MainActivity;->access$802(Lio/peakmood/mobile/MainActivity;Z)Z

    .line 359
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$900(Lio/peakmood/mobile/MainActivity;)V

    .line 360
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    const-string v1, "\u041a\u0430\u0440\u0442\u0430 \u0430\u043a\u0442\u0438\u0432\u043d\u0430. \u041d\u0430\u0445\u043e\u0434\u043a\u0438 \u0431\u0443\u0434\u0443\u0442 \u043f\u043e\u044f\u0432\u043b\u044f\u0442\u044c\u0441\u044f \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u043f\u043e \u043c\u0435\u0440\u0435 \u0434\u0432\u0438\u0436\u0435\u043d\u0438\u044f."

    const-string v2, "\u0412 \u0421\u0415\u0422\u0418"

    const-string v3, "\u041f\u043e\u043b\u0435\u0432\u043e\u0439 \u0440\u0435\u0436\u0438\u043c \u0433\u043e\u0442\u043e\u0432"

    invoke-static {v0, v3, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1000(Lio/peakmood/mobile/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    .line 365
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v0}, Lio/peakmood/mobile/MainActivity;->access$1100(Lio/peakmood/mobile/MainActivity;)Landroid/location/Location;

    move-result-object v0

    if-eqz v0, :cond_0

    .line 366
    iget-object v0, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v0, v0, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    new-instance v1, Landroid/location/Location;

    iget-object v2, p0, Lio/peakmood/mobile/MainActivity$5$1;->this$1:Lio/peakmood/mobile/MainActivity$5;

    iget-object v2, v2, Lio/peakmood/mobile/MainActivity$5;->this$0:Lio/peakmood/mobile/MainActivity;

    invoke-static {v2}, Lio/peakmood/mobile/MainActivity;->access$1100(Lio/peakmood/mobile/MainActivity;)Landroid/location/Location;

    move-result-object v2

    invoke-direct {v1, v2}, Landroid/location/Location;-><init>(Landroid/location/Location;)V

    const/4 v2, 0x1

    invoke-static {v0, v1, v2}, Lio/peakmood/mobile/MainActivity;->access$1200(Lio/peakmood/mobile/MainActivity;Landroid/location/Location;Z)V

    .line 368
    :cond_0
    return-void
.end method
