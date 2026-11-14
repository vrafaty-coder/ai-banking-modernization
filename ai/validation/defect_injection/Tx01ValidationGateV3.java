package banking.tx01;

import java.util.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;

/** Independent, explicit COBOL-derived oracle; no modifications to generated Java. */
public class Tx01ValidationGateV3 {
  static final String ID="0000000000001", PREFIX="20261111091530TERM";
  static class Accounts implements AccountRepository {
    AccountRecord record=new AccountRecord(ID,"A","IRR",1000);
    boolean openError, readIoError, updateError, failRewrite, failRollback;
    int reads,writes;
    public AccountRecord read(String id){reads++;return readIoError?null:(record!=null&&record.accountNumber().equals(id)?record:null);}
    public void rewrite(AccountRecord r){writes++;if(failRewrite||(failRollback&&writes==2)){updateError=true;return;}record=r;}
    public boolean hasOpenError(){return openError;}
    public boolean hasUpdateError(){return updateError;}
  }
  static class Journals implements JournalRepository {
    Map<String,JournalRecord> records=new HashMap<>();
    boolean openError,lookupError,writeError;
    int reads,writes;
    public JournalRecord read(String stamp){reads++;return records.get(stamp);}
    public void write(JournalRecord r){writes++;if(!writeError)records.put(r.stamp(),r);}
    public boolean hasOpenError(){return openError;}
    public boolean hasWriteError(){return writeError;}
    public boolean hasFileError(){return lookupError;}
  }
  static class Scenario {
    String id,name,expectedMessage,expectedStamp="";
    long amount=250, expectedBalance=0, finalBalance=1000;
    String seq="0001";
    int status=1,alert=0,expectedJournalCount=0,expectedRewrites=-1;
    boolean evaluable=true, expectedJournalContent=false;
    Accounts a=new Accounts(); Journals j=new Journals();
    Scenario(String id,String name,String message,int alert){this.id=id;this.name=name;this.expectedMessage=message;this.alert=alert;}
  }
  static final List<String[]> rows=new ArrayList<>();
  static void emit(Scenario s,String dimension,String result,String details){rows.add(new String[]{s.id,s.name,dimension,result,details});}
  static String clean(String s){return s==null?"":s.trim();}
  static boolean response(Scenario s,Tx01Response r){
    return r.transactionCode().equals("TX01")&&r.statusCode()==s.status&&r.alertCode()==s.alert
      &&clean(r.alertMessage()).equals(s.expectedMessage)&&r.accountBalance()==s.expectedBalance
      &&clean(r.journalStamp()).equals(s.expectedStamp);
  }
  static void evaluate(Scenario s){
    Tx01Response r;
    try {r=new Tx01Service(s.a,s.j).execute(new Tx01Request("TX01","20261111","091530","TERM",s.seq,ID,s.amount));}
    catch(Exception ex){for(String d:new String[]{"RESPONSE","ACCOUNT","JOURNAL","BUSINESS_RULE"})emit(s,d,"FAIL","Exception: "+ex);return;}
    if(!s.evaluable){
      // The generated repository contract cannot represent distinct COBOL read file statuses 23 vs other.
      for(String d:new String[]{"RESPONSE","ACCOUNT","JOURNAL","BUSINESS_RULE"})emit(s,d,"NOT_EVALUABLE","read() returns null for both missing account and I/O error; actual alert="+r.alertCode());
      return;
    }
    boolean resp=response(s,r);
    emit(s,"RESPONSE",resp?"PASS":"FAIL",resp?"matches COBOL oracle":"actual="+r+" expected alert="+s.alert+" message="+s.expectedMessage);
    boolean account=(s.a.record==null ? s.id.equals("S03") : s.a.record.balance()==s.finalBalance) &&(s.expectedRewrites<0||s.a.writes==s.expectedRewrites);
    emit(s,"ACCOUNT",account?"PASS":"FAIL","balance="+(s.a.record==null?"null":s.a.record.balance())+" rewrites="+s.a.writes);
    boolean journal=s.j.records.size()==s.expectedJournalCount;
    if(journal&&s.expectedJournalContent){
      JournalRecord jr=s.j.records.get(s.expectedStamp);
      journal=jr!=null&&jr.stamp().equals(s.expectedStamp)&&jr.transactionCode().equals("TX01")&&jr.creditAccount().equals(ID)
         &&clean(jr.debitAccount()).isEmpty()&&jr.amount()==s.amount;
    }
    emit(s,"JOURNAL",journal?"PASS":"FAIL","count="+s.j.records.size()+" contentChecked="+s.expectedJournalContent);
    boolean rule=resp&&account&&journal;
    emit(s,"BUSINESS_RULE",rule?"PASS":"FAIL","composite of response, account and journal checks for this rule");
  }
  static String csv(String s){return "\""+s.replace("\"","\"\"").replace("\n"," ").replace("\r"," ")+"\"";}
  static String json(String s){return "\""+s.replace("\\","\\\\").replace("\"","\\\"").replace("\n","\\n").replace("\r","\\r")+"\"";}
  public static void main(String[] args)throws Exception{
    List<Scenario> cases=new ArrayList<>(); Scenario s;
    s=new Scenario("S01","Successful deposit","",0);s.status=0;s.expectedBalance=1250;s.finalBalance=1250;s.expectedStamp=PREFIX+"0001";s.expectedJournalCount=1;s.expectedJournalContent=true;s.expectedRewrites=1;cases.add(s);
    s=new Scenario("S02","Zero amount","Invalid amount",1004);s.amount=0;s.expectedRewrites=0;cases.add(s);
    s=new Scenario("S03","Missing account","Account not found",1001);s.a.record=null;cases.add(s);
    s=new Scenario("S04","Blocked account","Account blocked",1002);s.a.record=new AccountRecord(ID,"B","IRR",1000);cases.add(s);
    s=new Scenario("S05","Closed account","Account closed",1003);s.a.record=new AccountRecord(ID,"C","IRR",1000);cases.add(s);
    s=new Scenario("S06","Invalid account status","Invalid account status",9001);s.a.record=new AccountRecord(ID,"X","IRR",1000);cases.add(s);
    s=new Scenario("S07","Balance overflow","Balance overflow",1005);s.a.record=new AccountRecord(ID,"A","IRR",999999999999999L);s.amount=1;s.finalBalance=999999999999999L;cases.add(s);
    s=new Scenario("S08","Stamp collision","",0);s.status=0;s.expectedBalance=1250;s.finalBalance=1250;s.expectedStamp=PREFIX+"0002";s.expectedJournalCount=2;s.expectedJournalContent=true;s.j.records.put(PREFIX+"0001",new JournalRecord(PREFIX+"0001","TX01",ID,"",1));cases.add(s);
    s=new Scenario("S09","Stamp exhaustion","Journal stamp exhausted",1006);s.seq="9999";s.expectedJournalCount=1;s.j.records.put(PREFIX+"9999",new JournalRecord(PREFIX+"9999","TX01",ID,"",1));cases.add(s);
    s=new Scenario("S10","Journal write error rollback","Journal write error",9002);s.j.writeError=true;s.expectedRewrites=2;cases.add(s);
    s=new Scenario("S11","Account rewrite failure","Account update error",9001);s.a.failRewrite=true;s.expectedRewrites=1;cases.add(s);
    s=new Scenario("S12","Rollback rewrite failure","Journal write error",9002);s.j.writeError=true;s.a.failRollback=true;s.finalBalance=1250;s.expectedRewrites=2;cases.add(s);
    s=new Scenario("S13","Account open error","Account file error",9001);s.a.openError=true;s.expectedRewrites=0;cases.add(s);
    s=new Scenario("S14","Journal open error","Journal file error",9002);s.j.openError=true;s.expectedRewrites=0;cases.add(s);
    s=new Scenario("S15","Journal lookup I/O error","Journal file error",9002);s.j.lookupError=true;s.expectedRewrites=0;cases.add(s);
    s=new Scenario("S16","Account read I/O error","Account file error",9001);s.a.readIoError=true;s.evaluable=false;cases.add(s);
    for(Scenario c:cases)evaluate(c);
    StringBuilder csvOut=new StringBuilder("scenario_id,scenario,dimension,result,details\n");
    StringBuilder jsonOut=new StringBuilder("{\n  \"oracle\": \"TX01.cbl source-derived expected behavior; not a live COBOL execution\",\n  \"rows\": [\n");
    Map<String,int[]> totals=new LinkedHashMap<>();
    for(int i=0;i<rows.size();i++){
      String[] row=rows.get(i);
      for(int k=0;k<row.length;k++){if(k>0)csvOut.append(',');csvOut.append(csv(row[k]));}csvOut.append('\n');
      jsonOut.append("    {\"scenario_id\": ").append(json(row[0])).append(", \"scenario\": ").append(json(row[1]))
       .append(", \"dimension\": ").append(json(row[2])).append(", \"result\": ").append(json(row[3]))
       .append(", \"details\": ").append(json(row[4])).append("}").append(i+1<rows.size()?",":"").append('\n');
      int[] t=totals.computeIfAbsent(row[2],k->new int[3]);t[row[3].equals("PASS")?0:row[3].equals("FAIL")?1:2]++;
    }
    jsonOut.append("  ],\n  \"summary\": {\n");int idx=0;
    for(var e:totals.entrySet()){int[] t=e.getValue();jsonOut.append("    ").append(json(e.getKey())).append(": {\"PASS\": ").append(t[0]).append(", \"FAIL\": ").append(t[1]).append(", \"NOT_EVALUABLE\": ").append(t[2]).append("}").append(++idx<totals.size()?",":"").append('\n');}
    jsonOut.append("  }\n}\n");
    Files.writeString(Path.of("tx01_validation_gate_v3_results.csv"),csvOut,StandardCharsets.UTF_8);
    Files.writeString(Path.of("tx01_validation_gate_v3_results.json"),jsonOut,StandardCharsets.UTF_8);
    for(var e:totals.entrySet()){int[] t=e.getValue();System.out.println(e.getKey()+": PASS="+t[0]+" FAIL="+t[1]+" NOT_EVALUABLE="+t[2]);}
    System.out.println("Scenarios="+cases.size()+"; generated CSV and JSON. NOT_EVALUABLE is excluded from equivalence claims.");
  }
}
