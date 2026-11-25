import java.util.Random;
public class RandCheck {
  public static void main(String[] a) {
    Random r = new Random(1);
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < 5; i++) sb.append(r.nextInt(5)).append(' ');
    for (int i = 0; i < 3; i++) sb.append(r.nextDouble()).append(' ');
    for (int i = 0; i < 5; i++) sb.append(r.nextInt(731 - i)).append(' ');
    for (int i = 0; i < 3; i++) sb.append(r.nextInt(8)).append(' ');
    for (int i = 0; i < 3; i++) sb.append(r.nextInt(1000000007)).append(' ');
    System.out.println(sb.toString().trim());
  }
}
